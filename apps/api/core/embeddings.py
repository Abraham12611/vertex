from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("BAAI/bge-base-en-v1.5")

def embed(texts: list[str]) -> list[list[float]]:
    return _model.encode(texts, normalize_embeddings=True).tolist()