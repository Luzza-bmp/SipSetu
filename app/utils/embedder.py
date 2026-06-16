
from __future__ import annotations
from typing import List
import numpy as np
 
_model = None   # module-level singleton
 
 
def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        # ~80 MB download on first run; cached in ~/.cache/huggingface afterwards
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model
 
 
def embed_text(text: str) -> List[float]:
    """
    Return a 384-dimensional unit-normalised float list for `text`.
    pgvector's `<=>` operator expects a plain Python list or numpy array.
    """
    model = _get_model()
    vector: np.ndarray = model.encode(text, normalize_embeddings=True)
    return vector.tolist()