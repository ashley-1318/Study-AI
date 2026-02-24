"""StudyAI — embedding and FAISS vector store tools."""


# ─── tools/embedder.py content ─────────────────────────────────────────────
"""Singleton SentenceTransformer embedder used across all agents."""
from sentence_transformers import SentenceTransformer

# Load once at module import; all-MiniLM-L6-v2 → 384-dim vectors
_model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(text: str) -> list:
    """Encode a single string into a 384-dim float list."""
    return _model.encode(text, convert_to_numpy=True).tolist()


def generate_embeddings(texts: list) -> list:
    """Batch-encode a list of strings into 384-dim float lists."""
    return _model.encode(texts, convert_to_numpy=True).tolist()
