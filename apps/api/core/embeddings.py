from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
from core.settings import settings

_model = None

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model

def embed(texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
    """Generate embeddings for text(s)"""
    model = _get_model()

    if isinstance(texts, str):
        texts = [texts]

    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()

def embed_single(text: str) -> List[float]:
    """Generate embedding for a single text"""
    return embed(text)[0]

def similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """Calculate cosine similarity between two embeddings"""
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    return float(np.dot(vec1, vec2))

def batch_embed(texts: List[str], batch_size: int = 32) -> List[List[float]]:
    """Generate embeddings for a batch of texts"""
    model = _get_model()
    embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_embeddings = model.encode(batch, normalize_embeddings=True)
        embeddings.extend(batch_embeddings.tolist())

    return embeddings