from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from api.v1.deps import get_current_user
from db.base import SessionLocal
from db.models.user import User
from db.models.document import Document
from db.models.chunk import Chunk
from db.models.content_item import ContentItem
from core.embeddings import embed
from sqlalchemy import text
from sqlalchemy.future import select

router = APIRouter()

# Pydantic models
class SearchRequest(BaseModel):
    query: str
    project_id: Optional[UUID] = None
    document_ids: Optional[List[UUID]] = None
    content_types: Optional[List[str]] = None
    top_k: int = 10
    threshold: float = 0.7
    include_metadata: bool = True

class SearchResult(BaseModel):
    content: str
    score: float
    source_type: str
    source_id: UUID
    metadata: Dict[str, Any] = {}

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int
    search_time: float
    suggestions: List[str] = []

# Search endpoints
@router.post("/semantic", response_model=SearchResponse)
async def semantic_search(
    request: SearchRequest,
    current_user: User = Depends(get_current_user)
):
    """Semantic search across documents and content."""
    import time
    start_time = time.time()

    try:
        # Generate embedding for query
        q_emb = await embed([request.query])

        async with SessionLocal() as session:
            # Build search query
            sql = """
                SELECT
                    c.content,
                    1 - (c.embedding <=> :q_emb) AS score,
                    'chunk' as source_type,
                    c.document_id as source_id,
                    d.filename,
                    d.document_type,
                    c.chunk_idx
                FROM chunks c
                JOIN documents d ON c.document_id = d.id
                WHERE 1=1
            """
            params = {"q_emb": q_emb[0], "k": request.top_k}

            if request.project_id:
                sql += " AND d.project_id = :project_id"
                params["project_id"] = request.project_id

            if request.document_ids:
                sql += " AND c.document_id = ANY(:document_ids)"
                params["document_ids"] = request.document_ids

            sql += " ORDER BY c.embedding <=> :q_emb ASC LIMIT :k"

            result = await session.execute(text(sql), params)
            rows = result.fetchall()

            # Process results
            results = []
            for row in rows:
                if row[1] >= request.threshold:  # score >= threshold
                    metadata = {
                        "filename": row[4],
                        "document_type": row[5],
                        "chunk_idx": row[6]
                    } if request.include_metadata else {}

                    results.append(SearchResult(
                        content=row[0],
                        score=row[1],
                        source_type=row[2],
                        source_id=row[3],
                        metadata=metadata
                    ))

            search_time = time.time() - start_time

            return SearchResponse(
                query=request.query,
                results=results,
                total_results=len(results),
                search_time=search_time,
                suggestions=[]  # Could implement query suggestions
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@router.post("/keyword", response_model=SearchResponse)
async def keyword_search(
    request: SearchRequest,
    current_user: User = Depends(get_current_user)
):
    """Keyword-based search across documents and content."""
    import time
    start_time = time.time()

    async with SessionLocal() as session:
        # Build keyword search query
        query = select(Chunk).join(Document)

        if request.project_id:
            query = query.where(Document.project_id == request.project_id)

        if request.document_ids:
            query = query.where(Chunk.document_id.in_(request.document_ids))

        # Simple keyword matching (could be enhanced with full-text search)
        query = query.where(Chunk.content.ilike(f"%{request.query}%"))
        query = query.limit(request.top_k)

        result = await session.execute(query)
        chunks = result.scalars().all()

        results = []
        for chunk in chunks:
            # Simple relevance scoring based on keyword frequency
            keyword_count = chunk.content.lower().count(request.query.lower())
            score = min(1.0, keyword_count / 10.0)  # Normalize score

            if score >= request.threshold:
                metadata = {
                    "chunk_idx": chunk.chunk_idx,
                    "keyword_matches": keyword_count
                } if request.include_metadata else {}

                results.append(SearchResult(
                    content=chunk.content,
                    score=score,
                    source_type="chunk",
                    source_id=chunk.document_id,
                    metadata=metadata
                ))

        search_time = time.time() - start_time

        return SearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            search_time=search_time,
            suggestions=[]
        )

@router.post("/hybrid", response_model=SearchResponse)
async def hybrid_search(
    request: SearchRequest,
    semantic_weight: float = 0.7,
    keyword_weight: float = 0.3,
    current_user: User = Depends(get_current_user)
):
    """Hybrid search combining semantic and keyword search."""
    import time
    start_time = time.time()

    # Get semantic results
    semantic_request = SearchRequest(
        query=request.query,
        project_id=request.project_id,
        document_ids=request.document_ids,
        top_k=request.top_k * 2,  # Get more results for ranking
        threshold=0.5  # Lower threshold for hybrid
    )
    semantic_response = await semantic_search(semantic_request, current_user)

    # Get keyword results
    keyword_request = SearchRequest(
        query=request.query,
        project_id=request.project_id,
        document_ids=request.document_ids,
        top_k=request.top_k * 2,
        threshold=0.3
    )
    keyword_response = await keyword_search(keyword_request, current_user)

    # Combine and rank results
    combined_results = {}

    # Add semantic results
    for result in semantic_response.results:
        combined_results[result.source_id] = {
            "content": result.content,
            "semantic_score": result.score,
            "keyword_score": 0.0,
            "source_type": result.source_type,
            "source_id": result.source_id,
            "metadata": result.metadata
        }

    # Add keyword results and combine scores
    for result in keyword_response.results:
        if result.source_id in combined_results:
            combined_results[result.source_id]["keyword_score"] = result.score
        else:
            combined_results[result.source_id] = {
                "content": result.content,
                "semantic_score": 0.0,
                "keyword_score": result.score,
                "source_type": result.source_type,
                "source_id": result.source_id,
                "metadata": result.metadata
            }

    # Calculate hybrid scores and sort
    hybrid_results = []
    for result_data in combined_results.values():
        hybrid_score = (
            result_data["semantic_score"] * semantic_weight +
            result_data["keyword_score"] * keyword_weight
        )

        if hybrid_score >= request.threshold:
            hybrid_results.append(SearchResult(
                content=result_data["content"],
                score=hybrid_score,
                source_type=result_data["source_type"],
                source_id=result_data["source_id"],
                metadata=result_data["metadata"]
            ))

    # Sort by hybrid score and limit results
    hybrid_results.sort(key=lambda x: x.score, reverse=True)
    hybrid_results = hybrid_results[:request.top_k]

    search_time = time.time() - start_time

    return SearchResponse(
        query=request.query,
        results=hybrid_results,
        total_results=len(hybrid_results),
        search_time=search_time,
        suggestions=[]
    )

# Search analytics and suggestions
@router.get("/suggestions")
async def get_search_suggestions(
    query: str,
    limit: int = 5,
    current_user: User = Depends(get_current_user)
):
    """Get search suggestions based on query."""
    # For demo, return simple suggestions
    suggestions = [
        f"{query} tutorial",
        f"{query} examples",
        f"{query} best practices",
        f"{query} documentation",
        f"{query} guide"
    ]

    return {"suggestions": suggestions[:limit]}

@router.get("/popular-searches")
async def get_popular_searches(
    project_id: Optional[UUID] = None,
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """Get popular search terms."""
    # For demo, return mock popular searches
    popular_searches = [
        "FastAPI tutorial",
        "DevRel strategy",
        "content marketing",
        "community engagement",
        "analytics dashboard",
        "API documentation",
        "developer experience",
        "technical writing",
        "social media",
        "SEO optimization"
    ]

    return {"popular_searches": popular_searches[:limit]}

# Search history and analytics
@router.get("/history")
async def get_search_history(
    project_id: Optional[UUID] = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Get user's search history."""
    # For demo, return mock search history
    history = [
        {
            "query": "FastAPI authentication",
            "timestamp": datetime.now().isoformat(),
            "results_count": 5,
            "project_id": project_id
        },
        {
            "query": "DevRel best practices",
            "timestamp": datetime.now().isoformat(),
            "results_count": 8,
            "project_id": project_id
        }
    ]

    return {"history": history[:limit]}

@router.delete("/history")
async def clear_search_history(
    current_user: User = Depends(get_current_user)
):
    """Clear user's search history."""
    # For demo, just return success
    return {"message": "Search history cleared successfully"}
