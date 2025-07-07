from worker.celery_worker import celery_app
from db.base import SessionLocal
from db.models.chunk import Chunk
from db.models.document import Document
from core.embeddings import embed
from uuid import uuid4

@celery_app.task
def index_document_task(document_id, chunks):
    embeddings = embed(chunks)
    async with SessionLocal() as session:
        for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            chunk_obj = Chunk(
                id=uuid4(),
                document_id=document_id,
                chunk_idx=idx,
                content=chunk,
                embedding=emb
            )
            session.add(chunk_obj)
        await session.commit()
