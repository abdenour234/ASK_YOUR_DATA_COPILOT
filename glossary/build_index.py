"""
Sprint 1 - Ticket 4: FAISS Index Builder
Generates embeddings for business glossary and creates FAISS index for RAG retrieval.

Dependency: glossary/business_terms.yaml
"""

import yaml
import numpy as np
import faiss
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Tuple


class GlossaryIndexBuilder:
    """Builds FAISS index from business glossary for semantic search."""
    
    def __init__(
        self,
        glossary_path: str = "glossary/business_terms.yaml",
        model_name: str = "all-MiniLM-L6-v2",
        index_output_path: str = "glossary/glossary.index",
        metadata_output_path: str = "glossary/glossary_metadata.pkl"
    ):
        """
        Initialize the index builder.
        
        Args:
            glossary_path: Path to business glossary YAML file
            model_name: Sentence-transformers model for embeddings
            index_output_path: Where to save FAISS index
            metadata_output_path: Where to save metadata (text + glossary entries)
        """
        self.glossary_path = Path(glossary_path)
        self.model_name = model_name
        self.index_output_path = Path(index_output_path)
        self.metadata_output_path = Path(metadata_output_path)
        
        self.model = None
        self.glossary_data = None
        self.documents = []  # List of text chunks to embed
        self.metadata = []   # List of metadata dicts for each document
    
    def load_glossary(self) -> None:
        """Load glossary YAML file."""
        print(f"📖 Loading glossary from: {self.glossary_path}")
        
        with open(self.glossary_path, 'r', encoding='utf-8') as f:
            self.glossary_data = yaml.safe_load(f)
        
        print(f"✓ Loaded glossary version: {self.glossary_data.get('version', 'unknown')}")
        print(f"✓ Domain: {self.glossary_data.get('domain', 'unknown')}")
    
    def load_model(self) -> None:
        """Load sentence-transformers model for embeddings."""
        print(f"\n🤖 Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        print(f"✓ Model loaded (dimension: {self.model.get_sentence_embedding_dimension()})")
    
    def prepare_documents(self) -> None:
        """
        Convert glossary entries into searchable text documents.
        Each metric, dimension, business term becomes a document.
        """
        print("\n📝 Preparing documents from glossary...")
        
        # Process metrics
        if 'metrics' in self.glossary_data:
            for name, details in self.glossary_data['metrics'].items():
                # Create rich text description for embedding
                doc_text = self._create_metric_text(name, details)
                self.documents.append(doc_text)
                
                # Store metadata for retrieval
                self.metadata.append({
                    'type': 'metric',
                    'name': name,
                    'description': details.get('description', ''),
                    'sql_column': details.get('sql_column', ''),
                    'table': details.get('table', ''),
                    'aggregation': details.get('aggregation', ''),
                    'formula': details.get('formula', ''),
                    'unit': details.get('unit', ''),
                    'aliases': details.get('aliases', []),
                    'example_query': details.get('example_query', '')
                })
        
        # Process dimensions
        if 'dimensions' in self.glossary_data:
            for name, details in self.glossary_data['dimensions'].items():
                doc_text = self._create_dimension_text(name, details)
                self.documents.append(doc_text)
                
                self.metadata.append({
                    'type': 'dimension',
                    'name': name,
                    'description': details.get('description', ''),
                    'sql_column': details.get('sql_column', ''),
                    'table': details.get('table', ''),
                    'data_type': details.get('data_type', ''),
                    'possible_values': details.get('possible_values', []),
                    'example_query': details.get('example_query', '')
                })
        
        # Process business terms
        if 'business_terms' in self.glossary_data:
            for name, details in self.glossary_data['business_terms'].items():
                doc_text = self._create_business_term_text(name, details)
                self.documents.append(doc_text)
                
                self.metadata.append({
                    'type': 'business_term',
                    'name': name,
                    'description': details.get('description', ''),
                    'maps_to': details.get('maps_to', ''),
                    'requires': details.get('requires', [])
                })
        
        # Process common queries
        if 'common_queries' in self.glossary_data:
            for i, query_info in enumerate(self.glossary_data['common_queries']):
                doc_text = self._create_common_query_text(query_info)
                self.documents.append(doc_text)
                
                self.metadata.append({
                    'type': 'common_query',
                    'query': query_info.get('query', ''),
                    'intent': query_info.get('intent', ''),
                    'metrics': query_info.get('metrics', []),
                    'dimensions': query_info.get('dimensions', []),
                    'sql_pattern': query_info.get('sql_pattern', '')
                })
        
        print(f"✓ Prepared {len(self.documents)} documents")
        print(f"  - Metrics: {len([m for m in self.metadata if m['type'] == 'metric'])}")
        print(f"  - Dimensions: {len([m for m in self.metadata if m['type'] == 'dimension'])}")
        print(f"  - Business terms: {len([m for m in self.metadata if m['type'] == 'business_term'])}")
        print(f"  - Common queries: {len([m for m in self.metadata if m['type'] == 'common_query'])}")
    
    def _create_metric_text(self, name: str, details: Dict) -> str:
        """Create searchable text for a metric."""
        parts = [
            f"Metric: {name}",
            details.get('description', ''),
            f"Column: {details.get('sql_column', '')}",
            f"Aggregation: {details.get('aggregation', '')}",
            f"Formula: {details.get('formula', '')}",
            f"Unit: {details.get('unit', '')}",
            f"Example: {details.get('example_query', '')}"
        ]
        
        # Add aliases
        if 'aliases' in details:
            parts.append(f"Aliases: {', '.join(details['aliases'])}")
        
        return " | ".join([p for p in parts if p and not p.endswith(': ')])
    
    def _create_dimension_text(self, name: str, details: Dict) -> str:
        """Create searchable text for a dimension."""
        parts = [
            f"Dimension: {name}",
            details.get('description', ''),
            f"Column: {details.get('sql_column', '')}",
            f"Table: {details.get('table', '')}",
            f"Example: {details.get('example_query', '')}"
        ]
        
        # Add possible values if available
        if 'possible_values' in details and details['possible_values']:
            values = ', '.join(details['possible_values'][:5])  # First 5 values
            parts.append(f"Values: {values}")
        
        return " | ".join([p for p in parts if p and not p.endswith(': ')])
    
    def _create_business_term_text(self, name: str, details: Dict) -> str:
        """Create searchable text for a business term."""
        parts = [
            f"Business term: {name}",
            details.get('description', ''),
            f"Maps to: {details.get('maps_to', '')}",
            f"Type: {details.get('type', '')}"
        ]
        
        if 'requires' in details and details['requires']:
            parts.append(f"Requires: {', '.join(details['requires'])}")
        
        return " | ".join([p for p in parts if p and not p.endswith(': ')])
    
    def _create_common_query_text(self, query_info: Dict) -> str:
        """Create searchable text for common query patterns."""
        parts = [
            f"Query: {query_info.get('query', '')}",
            f"Intent: {query_info.get('intent', '')}",
            f"Metrics: {', '.join(query_info.get('metrics', []))}",
            f"Dimensions: {', '.join(query_info.get('dimensions', []))}",
            f"SQL pattern: {query_info.get('sql_pattern', '')}"
        ]
        
        return " | ".join([p for p in parts if p and not p.endswith(': ')])
    
    def create_embeddings(self) -> np.ndarray:
        """Generate embeddings for all documents."""
        print("\n🧮 Generating embeddings...")
        print(f"   Model: {self.model_name}")
        print(f"   Documents: {len(self.documents)}")
        
        # Generate embeddings (batched for efficiency)
        embeddings = self.model.encode(
            self.documents,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True  # L2 normalization for cosine similarity
        )
        
        print(f"✓ Generated embeddings shape: {embeddings.shape}")
        return embeddings
    
    def build_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        """
        Build FAISS index for fast similarity search.
        
        Args:
            embeddings: numpy array of embeddings (n_docs, embedding_dim)
        
        Returns:
            FAISS index
        """
        print("\n🔍 Building FAISS index...")
        
        dimension = embeddings.shape[1]
        
        # Use IndexFlatIP for inner product (cosine similarity with normalized vectors)
        index = faiss.IndexFlatIP(dimension)
        
        # Add embeddings to index
        index.add(embeddings.astype('float32'))
        
        print(f"✓ FAISS index created")
        print(f"   Dimension: {dimension}")
        print(f"   Total vectors: {index.ntotal}")
        
        return index
    
    def save_index(self, index: faiss.Index) -> None:
        """Save FAISS index and metadata to disk."""
        print("\n💾 Saving index and metadata...")
        
        # Ensure output directory exists
        self.index_output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(index, str(self.index_output_path))
        print(f"✓ Saved FAISS index: {self.index_output_path}")
        
        # Save metadata (documents + glossary entries)
        metadata_bundle = {
            'documents': self.documents,
            'metadata': self.metadata,
            'model_name': self.model_name,
            'glossary_version': self.glossary_data.get('version', 'unknown'),
            'domain': self.glossary_data.get('domain', 'unknown')
        }
        
        with open(self.metadata_output_path, 'wb') as f:
            pickle.dump(metadata_bundle, f)
        
        print(f"✓ Saved metadata: {self.metadata_output_path}")
    
    def build(self) -> None:
        """Execute full index building pipeline."""
        print("=" * 70)
        print("FAISS Index Builder - Sprint 1, Ticket 4")
        print("=" * 70)
        
        try:
            # Load data
            self.load_glossary()
            self.load_model()
            
            # Prepare documents
            self.prepare_documents()
            
            # Generate embeddings
            embeddings = self.create_embeddings()
            
            # Build index
            index = self.build_faiss_index(embeddings)
            
            # Save outputs
            self.save_index(index)
            
            print("\n" + "=" * 70)
            print("✅ Index building completed successfully!")
            print("=" * 70)
            print(f"📁 Output files:")
            print(f"   - Index: {self.index_output_path}")
            print(f"   - Metadata: {self.metadata_output_path}")
            print(f"\n🔎 Ready for semantic search via RAG API")
            print("=" * 70)
            
        except Exception as e:
            print(f"\n❌ Error during index building: {e}")
            raise


def main():
    """Main entry point for index building."""
    builder = GlossaryIndexBuilder()
    builder.build()


if __name__ == "__main__":
    main()
