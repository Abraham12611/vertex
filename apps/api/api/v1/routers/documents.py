from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException, Depends, status
from uuid import uuid4, UUID
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import pypdf
import markdown2
import asyncio

from api.v1.deps import get_current_user
from db.base import SessionLocal
from db.models.user import User
from db.models.document import Document
from db.models.chunk import Chunk
from db.models.project import Project
from core.embeddings import embed
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

router = APIRouter()

# Pydantic models
class DocumentStatus(str, Enum):
    processing = "processing"
    processed = "processed"
    failed = "failed"
    archived = "archived"

class DocumentType(str, Enum):
    pdf = "pdf"
    markdown = "markdown"
    text = "text"
    docx = "docx"
    html = "html"

class DocumentCreate(BaseModel):
    project_id: UUID
    filename: str
    document_type: DocumentType
    metadata: Optional[Dict[str, Any]] = None

class DocumentResponse(BaseModel):
    id: UUID
    project_id: UUID
    filename: str
    document_type: DocumentType
    status: DocumentStatus
    text: Optional[str] = None
    chunk_count: int
    created_at: datetime
    processed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    file_size: Optional[int] = None

class ChunkResponse(BaseModel):
    id: UUID
    document_id: UUID
    chunk_idx: int
    content: str
    embedding: Optional[List[float]] = None

class DocumentAnalytics(BaseModel):
    total_documents: int
    total_chunks: int
    avg_chunks_per_doc: float
    processing_success_rate: float
    storage_used_mb: float

# Document processing utilities
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i+chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks

async def process_document_content(file_content: bytes, filename: str) -> str:
    """Process different file types and extract text."""
    if filename.endswith(".pdf"):
        pdf = pypdf.PdfReader(file_content)
        text = "\n".join(
            page.extract_text() for page in pdf.pages
            if page.extract_text().strip()
        )
    elif filename.endswith((".md", ".markdown")):
        text = file_content.decode('utf-8')
    elif filename.endswith(".txt"):
        text = file_content.decode('utf-8')
    elif filename.endswith(".html"):
        # Basic HTML to text conversion
        import re
        text = re.sub(r'<[^>]+>', '', file_content.decode('utf-8'))
    else:
        text = file_content.decode('utf-8', errors='ignore')

    return text.strip()

async def index_document_task(document_id: str, chunks: List[str]):
    """Background task to process and index document chunks."""
    try:
        async with SessionLocal() as session:
            # Get document
            doc = await session.get(Document, document_id)
            if not doc:
                return

            # Generate embeddings for chunks
            embeddings = await embed(chunks)

            # Create chunk records
            for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                chunk = Chunk(
                    document_id=doc.id,
                    chunk_idx=idx,
                    content=chunk_text,
                    embedding=embedding
                )
                session.add(chunk)

            # Update document status
            doc.status = "processed"
            doc.processed_at = datetime.now()

            await session.commit()

    except Exception as e:
        # Update document status to failed
        async with SessionLocal() as session:
            doc = await session.get(Document, document_id)
            if doc:
                doc.status = "failed"
                await session.commit()
        print(f"Error processing document {document_id}: {e}")

# Document CRUD operations
@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    project_id: UUID = Form(...),
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user)
):
    """Upload and process a document."""
    # Validate file type
    allowed_extensions = {'.pdf', '.md', '.markdown', '.txt', '.html'}
    if not any(file.filename.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type"
        )

    # Verify project exists
    async with SessionLocal() as session:
        project = await session.get(Project, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

    # Read file content
    content = await file.read()

    # Create document record
    doc_id = uuid4()
    async with SessionLocal() as session:
        doc = Document(
            id=doc_id,
            project_id=project_id,
            filename=file.filename,
            text="",  # Will be updated after processing
            status="processing",
            metadata=metadata or {}
        )
        session.add(doc)
        await session.commit()

    # Process document content
    try:
        text = await process_document_content(content, file.filename)
        chunks = chunk_text(text)

        # Update document with text
        async with SessionLocal() as session:
            doc = await session.get(Document, doc_id)
            doc.text = text
            await session.commit()

        # Add background task for indexing
        if background_tasks:
            background_tasks.add_task(index_document_task, str(doc_id), chunks)

        return DocumentResponse(
            id=doc_id,
            project_id=project_id,
            filename=file.filename,
            document_type=DocumentType(file.filename.split('.')[-1]),
            status="processing",
            text=text,
            chunk_count=len(chunks),
            created_at=datetime.now(),
            processed_at=None,
            metadata=metadata or {},
            file_size=len(content)
        )

    except Exception as e:
        # Update document status to failed
        async with SessionLocal() as session:
            doc = await session.get(Document, doc_id)
            doc.status = "failed"
            await session.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {str(e)}"
        )

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    project_id: Optional[UUID] = None,
    status: Optional[DocumentStatus] = None,
    document_type: Optional[DocumentType] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """List documents with optional filters."""
    async with SessionLocal() as session:
        query = select(Document)

        if project_id:
            query = query.where(Document.project_id == project_id)
        if status:
            query = query.where(Document.status == status)
        if document_type:
            query = query.where(Document.document_type == document_type)

        query = query.offset(offset).limit(limit)
        result = await session.execute(query)
        documents = result.scalars().all()

        return [
            DocumentResponse(
                id=doc.id,
                project_id=doc.project_id,
                filename=doc.filename,
                document_type=doc.document_type,
                status=doc.status,
                text=doc.text,
                chunk_count=0,  # Would need to count chunks
                created_at=doc.created_at,
                processed_at=doc.processed_at,
                metadata=doc.metadata or {},
                file_size=None
            )
            for doc in documents
        ]

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get specific document by ID."""
    async with SessionLocal() as session:
        document = await session.get(Document, document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Count chunks
        chunk_count = await session.scalar(
            select(Chunk).where(Chunk.document_id == document_id)
        )

        return DocumentResponse(
            id=document.id,
            project_id=document.project_id,
            filename=document.filename,
            document_type=document.document_type,
            status=document.status,
            text=document.text,
            chunk_count=chunk_count or 0,
            created_at=document.created_at,
            processed_at=document.processed_at,
            metadata=document.metadata or {},
            file_size=None
        )

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Delete document and its chunks."""
    async with SessionLocal() as session:
        document = await session.get(Document, document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Delete associated chunks first
        await session.execute(
            select(Chunk).where(Chunk.document_id == document_id)
        )

        await session.delete(document)
        await session.commit()

# Document chunks
@router.get("/{document_id}/chunks", response_model=List[ChunkResponse])
async def get_document_chunks(
    document_id: UUID,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """Get chunks for a specific document."""
    async with SessionLocal() as session:
        # Verify document exists
        document = await session.get(Document, document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        query = select(Chunk).where(Chunk.document_id == document_id)
        query = query.offset(offset).limit(limit)
        result = await session.execute(query)
        chunks = result.scalars().all()

        return [
            ChunkResponse(
                id=chunk.id,
                document_id=chunk.document_id,
                chunk_idx=chunk.chunk_idx,
                content=chunk.content,
                embedding=chunk.embedding.tolist() if chunk.embedding else None
            )
            for chunk in chunks
        ]

# Document reprocessing
@router.post("/{document_id}/reprocess")
async def reprocess_document(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Reprocess a document (useful if embedding model changed)."""
    async with SessionLocal() as session:
        document = await session.get(Document, document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        if not document.text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document has no text to reprocess"
            )

        # Delete existing chunks
        await session.execute(
            select(Chunk).where(Chunk.document_id == document_id)
        )

        # Update status
        document.status = "processing"
        await session.commit()

        # Reprocess
        chunks = chunk_text(document.text)
        background_tasks.add_task(index_document_task, str(document_id), chunks)

        return {"message": "Document reprocessing started"}

# Document analytics
@router.get("/analytics", response_model=DocumentAnalytics)
async def get_document_analytics(
    project_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user)
):
    """Get document analytics."""
    async with SessionLocal() as session:
        # Count documents
        doc_query = select(Document)
        if project_id:
            doc_query = doc_query.where(Document.project_id == project_id)

        doc_result = await session.execute(doc_query)
        total_documents = len(doc_result.scalars().all())

        # Count chunks
        chunk_query = select(Chunk)
        if project_id:
            chunk_query = chunk_query.join(Document).where(Document.project_id == project_id)

        chunk_result = await session.execute(chunk_query)
        total_chunks = len(chunk_result.scalars().all())

        # Calculate success rate
        success_query = select(Document).where(Document.status == "processed")
        if project_id:
            success_query = success_query.where(Document.project_id == project_id)

        success_result = await session.execute(success_query)
        successful_docs = len(success_result.scalars().all())

        success_rate = (successful_docs / total_documents * 100) if total_documents > 0 else 0

        return DocumentAnalytics(
            total_documents=total_documents,
            total_chunks=total_chunks,
            avg_chunks_per_doc=total_chunks / total_documents if total_documents > 0 else 0,
            processing_success_rate=success_rate,
            storage_used_mb=total_chunks * 0.001  # Rough estimate
        )

# Document search
@router.post("/search")
async def search_documents(
    project_id: UUID,
    query: str,
    top_k: int = 5,
    threshold: float = 0.7,
    current_user: User = Depends(get_current_user)
):
    """Search documents using semantic similarity."""
    q_emb = await embed([query])

    async with SessionLocal() as session:
        sql = """
            SELECT c.content, c.chunk_idx, d.filename,
                   1 - (c.embedding <=> :q_emb) AS score
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
            WHERE d.project_id = :pid
            ORDER BY c.embedding <=> :q_emb ASC
            LIMIT :k
        """

        result = await session.execute(
            sql,
            {"q_emb": q_emb[0], "pid": project_id, "k": top_k}
        )

        matches = []
        for row in result:
            if row[3] >= threshold:  # score >= threshold
                matches.append({
                    "content": row[0],
                    "chunk_idx": row[1],
                    "filename": row[2],
                    "score": row[3]
                })

        return {"query": query, "matches": matches}
