from fastapi import APIRouter
from core.embeddings import embed
from db.base import SessionLocal
from sqlalchemy import text

router = APIRouter()

@router.post("/search")
async def search(project_id: str, query: str, top_k: int = 5):
    q_emb = embed([query])[0]
    async with SessionLocal() as session:
        sql = text("""
            SELECT content, 1 - (embedding <=> :q_emb) AS score
            FROM chunks
            WHERE document_id IN (SELECT id FROM documents WHERE project_id = :pid)
            ORDER BY embedding <=> :q_emb ASC
            LIMIT :k
        """)
        results = await session.execute(sql, {"q_emb": q_emb, "pid": project_id, "k": top_k})
        matches = [{"content": row[0], "score": row[1]} for row in results]
    return {"matches": matches}
