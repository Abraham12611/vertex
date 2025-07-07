from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks
from uuid import uuid4
from db.base import SessionLocal
from db.models.document import Document
from db.models.chunk import Chunk
from core.embeddings import embed
import pypdf
import markdown2

router = APIRouter()

def chunk_text(text, chunk_size=500, overlap=50):
    # Simple whitespace chunking for demo; replace with token-based for prod
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i+chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

@router.post("/documents/upload")
async def upload_document(
    project_id: str = Form(...),
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    content = await file.read()
    if file.filename.endswith(".pdf"):
        pdf = pypdf.PdfReader(file.file)
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    elif file.filename.endswith(".md"):
        text = markdown2.markdown(content.decode())
    else:
        text = content.decode()

    chunks = chunk_text(text)
    doc_id = uuid4()
    async with SessionLocal() as session:
        doc = Document(id=doc_id, project_id=project_id, filename=file.filename, text=text)
        session.add(doc)
        await session.commit()
    if background_tasks:
        background_tasks.add_task(index_document_task, str(doc_id), chunks)
    return {"document_id": str(doc_id), "chunks_indexed": len(chunks)}
