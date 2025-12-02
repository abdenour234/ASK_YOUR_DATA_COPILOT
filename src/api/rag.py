"""
Simple RAG retriever - searches glossary for context
"""

import faiss
import pickle
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional


# Global state
_index = None
_documents = []
_metadata = []
_model = None


def load_glossary(
    index_path: str = "glossary/glossary.index",
    metadata_path: str = "glossary/glossary_metadata.pkl"
) -> None:
    """Load FAISS index and metadata."""
    global _index, _documents, _metadata, _model
    
    index_path = Path(index_path)
    metadata_path = Path(metadata_path)
    
    if not index_path.exists() or not metadata_path.exists():
        return  # Skip if not available
    
    _index = faiss.read_index(str(index_path))
    
    with open(metadata_path, 'rb') as f:
        bundle = pickle.load(f)
    
    _documents = bundle['documents']
    _metadata = bundle['metadata']
    model_name = bundle.get('model_name', 'all-MiniLM-L6-v2')
    _model = SentenceTransformer(model_name)


def search_glossary(query: str, top_k: int = 5) -> List[Dict]:
    """
    Search glossary for relevant context.
    
    Returns list of dicts with:
    - type: str
    - name: str
    - description: str
    - score: float
    """
    if _index is None or _model is None:
        load_glossary()
    
    if _index is None:
        return []  # No glossary available
    
    try:
        query_embedding = _model.encode([query])
        distances, indices = _index.search(query_embedding, top_k)
        
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(_metadata):
                meta = _metadata[idx]
                results.append({
                    'type': meta.get('type', 'unknown'),
                    'name': meta.get('name', ''),
                    'description': meta.get('description', ''),
                    'score': float(dist)
                })
        
        return results
    except Exception:
        return []
