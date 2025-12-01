"""
Sprint 1 - Ticket 4: RAG Retrieval System
Provides semantic search over business glossary using FAISS.

Dependency: glossary/glossary.index, glossary/glossary_metadata.pkl
"""

import faiss
import pickle
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
from pydantic import BaseModel


class RetrievalResult(BaseModel):
    """Single search result from glossary."""
    type: str
    name: str
    description: str
    score: float
    metadata: Dict
    
    class Config:
        arbitrary_types_allowed = True


class GlossaryRetriever:
    """Semantic search over business glossary for RAG."""
    
    def __init__(
        self,
        index_path: str = "glossary/glossary.index",
        metadata_path: str = "glossary/glossary_metadata.pkl",
        model_name: Optional[str] = None
    ):
        """
        Initialize the retriever.
        
        Args:
            index_path: Path to FAISS index file
            metadata_path: Path to metadata pickle file
            model_name: Sentence-transformers model (must match index builder)
        """
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)
        
        self.index = None
        self.documents = []
        self.metadata = []
        self.model = None
        self.model_name = model_name
        
        self._load_index()
        self._load_metadata()
        self._load_model()
    
    def _load_index(self) -> None:
        """Load FAISS index from disk."""
        if not self.index_path.exists():
            raise FileNotFoundError(f"FAISS index not found: {self.index_path}")
        
        self.index = faiss.read_index(str(self.index_path))
    
    def _load_metadata(self) -> None:
        """Load metadata (documents + glossary entries) from disk."""
        if not self.metadata_path.exists():
            raise FileNotFoundError(f"Metadata not found: {self.metadata_path}")
        
        with open(self.metadata_path, 'rb') as f:
            metadata_bundle = pickle.load(f)
        
        self.documents = metadata_bundle['documents']
        self.metadata = metadata_bundle['metadata']
        
        # Use model name from metadata if not provided
        if self.model_name is None:
            self.model_name = metadata_bundle.get('model_name', 'all-MiniLM-L6-v2')
    
    def _load_model(self) -> None:
        """Load sentence-transformers model for query encoding."""
        self.model = SentenceTransformer(self.model_name)
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter_type: Optional[str] = None
    ) -> List[RetrievalResult]:
        """
        Retrieve most relevant glossary entries for a query.
        
        Args:
            query: Natural language query
            top_k: Number of results to return
            filter_type: Optional filter ('metric', 'dimension', 'business_term', 'common_query')
        
        Returns:
            List of RetrievalResult objects sorted by relevance
        """
        # Encode query
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        ).astype('float32')
        
        # Search FAISS index (returns distances and indices)
        # Using inner product (cosine similarity with normalized vectors)
        distances, indices = self.index.search(query_embedding, top_k * 2)  # Get extra for filtering
        
        # Convert to results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):  # Valid index
                meta = self.metadata[idx]
                
                # Apply type filter if specified
                if filter_type and meta.get('type') != filter_type:
                    continue
                
                result = RetrievalResult(
                    type=meta.get('type', 'unknown'),
                    name=meta.get('name', meta.get('query', 'unnamed')),
                    description=meta.get('description', ''),
                    score=float(dist),  # Cosine similarity score (higher = more similar)
                    metadata=meta
                )
                results.append(result)
                
                # Stop once we have enough results
                if len(results) >= top_k:
                    break
        
        return results
    
    def retrieve_metrics(self, query: str, top_k: int = 3) -> List[RetrievalResult]:
        """Retrieve metric definitions relevant to query."""
        return self.retrieve(query, top_k=top_k, filter_type='metric')
    
    def retrieve_dimensions(self, query: str, top_k: int = 3) -> List[RetrievalResult]:
        """Retrieve dimension definitions relevant to query."""
        return self.retrieve(query, top_k=top_k, filter_type='dimension')
    
    def retrieve_business_terms(self, query: str, top_k: int = 3) -> List[RetrievalResult]:
        """Retrieve business term mappings relevant to query."""
        return self.retrieve(query, top_k=top_k, filter_type='business_term')
    
    def get_context_for_sql(self, query: str, top_k: int = 5) -> Dict:
        """
        Get comprehensive context for SQL generation.
        Returns metrics, dimensions, and relevant context.
        
        Args:
            query: Natural language query
            top_k: Number of total results
        
        Returns:
            Dictionary with categorized results
        """
        # Get top results across all types
        all_results = self.retrieve(query, top_k=top_k)
        
        # Categorize results
        context = {
            'query': query,
            'metrics': [],
            'dimensions': [],
            'business_terms': [],
            'common_patterns': [],
            'all_results': []
        }
        
        for result in all_results:
            context['all_results'].append({
                'type': result.type,
                'name': result.name,
                'description': result.description,
                'score': result.score,
                'sql_column': result.metadata.get('sql_column', ''),
                'table': result.metadata.get('table', ''),
                'formula': result.metadata.get('formula', ''),
                'aggregation': result.metadata.get('aggregation', '')
            })
            
            # Categorize by type
            if result.type == 'metric':
                context['metrics'].append({
                    'name': result.name,
                    'description': result.description,
                    'sql_column': result.metadata.get('sql_column', ''),
                    'table': result.metadata.get('table', ''),
                    'aggregation': result.metadata.get('aggregation', ''),
                    'formula': result.metadata.get('formula', ''),
                    'score': result.score
                })
            elif result.type == 'dimension':
                context['dimensions'].append({
                    'name': result.name,
                    'description': result.description,
                    'sql_column': result.metadata.get('sql_column', ''),
                    'table': result.metadata.get('table', ''),
                    'score': result.score
                })
            elif result.type == 'business_term':
                context['business_terms'].append({
                    'name': result.name,
                    'description': result.description,
                    'maps_to': result.metadata.get('maps_to', ''),
                    'requires': result.metadata.get('requires', []),
                    'score': result.score
                })
            elif result.type == 'common_query':
                context['common_patterns'].append({
                    'query': result.metadata.get('query', ''),
                    'intent': result.metadata.get('intent', ''),
                    'sql_pattern': result.metadata.get('sql_pattern', ''),
                    'score': result.score
                })
        
        return context


# Singleton instance for FastAPI
_retriever_instance = None


def get_retriever() -> GlossaryRetriever:
    """
    Get or create singleton retriever instance.
    Used for FastAPI dependency injection.
    """
    global _retriever_instance
    
    if _retriever_instance is None:
        _retriever_instance = GlossaryRetriever()
    
    return _retriever_instance
