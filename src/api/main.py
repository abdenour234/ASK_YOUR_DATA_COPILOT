"""
Sprint 1 - Ticket 4: FastAPI Application
Provides /retrieve endpoint for RAG-based glossary search.

Dependency: src/api/rag.py
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from src.api.rag import get_retriever, RetrievalResult
import uvicorn


# Pydantic models for request/response
class RetrieveRequest(BaseModel):
    """Request body for /retrieve endpoint."""
    query: str = Field(..., description="Natural language query", min_length=1)
    top_k: int = Field(5, description="Number of results to return", ge=1, le=20)
    filter_type: Optional[str] = Field(None, description="Filter by type: metric, dimension, business_term, common_query")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the total revenue?",
                "top_k": 5,
                "filter_type": None
            }
        }


class RetrieveResponse(BaseModel):
    """Response from /retrieve endpoint."""
    query: str
    top_k: int
    results: List[Dict]
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the total revenue?",
                "top_k": 5,
                "results": [
                    {
                        "type": "metric",
                        "name": "revenue",
                        "description": "Total payment value from completed orders",
                        "score": 0.89,
                        "metadata": {
                            "sql_column": "payment_value",
                            "table": "raw.order_payments",
                            "aggregation": "SUM"
                        }
                    }
                ]
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    index_loaded: bool
    total_entries: int


# Initialize FastAPI app
app = FastAPI(
    title="Ask Your Data - RAG API",
    description="Semantic search over business glossary for SQL generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check."""
    try:
        retriever = get_retriever()
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            index_loaded=retriever.index is not None,
            total_entries=len(retriever.metadata)
        )
    except Exception as e:
        return HealthResponse(
            status="error",
            version="1.0.0",
            index_loaded=False,
            total_entries=0
        )


@app.post("/retrieve", response_model=RetrieveResponse)
async def retrieve(request: RetrieveRequest):
    """
    Retrieve relevant glossary entries for a natural language query.
    
    This endpoint performs semantic search over the business glossary
    to find metrics, dimensions, and business terms relevant to the query.
    
    **Use Case**: Call this before SQL generation to get context about
    which tables, columns, and aggregations to use.
    """
    try:
        retriever = get_retriever()
        
        # Perform retrieval
        results = retriever.retrieve(
            query=request.query,
            top_k=request.top_k,
            filter_type=request.filter_type
        )
        
        # Convert to dict format for response
        results_dict = []
        for r in results:
            results_dict.append({
                "type": r.type,
                "name": r.name,
                "description": r.description,
                "score": round(r.score, 4),
                "metadata": r.metadata
            })
        
        return RetrieveResponse(
            query=request.query,
            top_k=request.top_k,
            results=results_dict
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")


@app.get("/retrieve", response_model=RetrieveResponse)
async def retrieve_get(
    query: str = Query(..., description="Natural language query", min_length=1),
    top_k: int = Query(5, description="Number of results", ge=1, le=20),
    filter_type: Optional[str] = Query(None, description="Filter by type")
):
    """
    GET version of /retrieve endpoint (for easy testing with curl/browser).
    
    Example:
        GET /retrieve?query=total revenue&top_k=3
    """
    request = RetrieveRequest(query=query, top_k=top_k, filter_type=filter_type)
    return await retrieve(request)


@app.get("/context/{query}")
async def get_sql_context(
    query: str,
    top_k: int = Query(5, description="Number of results", ge=1, le=20)
):
    """
    Get comprehensive context for SQL generation.
    
    Returns categorized results (metrics, dimensions, business terms, patterns)
    ready to be used in SQL generation prompts.
    
    Example:
        GET /context/show revenue by state
    """
    try:
        retriever = get_retriever()
        context = retriever.get_context_for_sql(query, top_k=top_k)
        return context
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context error: {str(e)}")


@app.get("/metrics")
async def list_metrics(
    query: Optional[str] = Query(None, description="Search query for metrics"),
    top_k: int = Query(10, description="Number of results", ge=1, le=50)
):
    """
    List or search available metrics.
    
    Examples:
        GET /metrics - List all metrics
        GET /metrics?query=sales&top_k=5 - Search for sales-related metrics
    """
    try:
        retriever = get_retriever()
        
        if query:
            results = retriever.retrieve_metrics(query, top_k=top_k)
        else:
            # Return all metrics
            results = [r for r in retriever.metadata if r.get('type') == 'metric'][:top_k]
            results = [RetrievalResult(
                type=r['type'],
                name=r['name'],
                description=r.get('description', ''),
                score=1.0,
                metadata=r
            ) for r in results]
        
        return {
            "query": query or "all",
            "count": len(results),
            "metrics": [
                {
                    "name": r.name,
                    "description": r.description,
                    "sql_column": r.metadata.get('sql_column', ''),
                    "table": r.metadata.get('table', ''),
                    "aggregation": r.metadata.get('aggregation', ''),
                    "unit": r.metadata.get('unit', ''),
                    "score": r.score
                }
                for r in results
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics error: {str(e)}")


@app.get("/dimensions")
async def list_dimensions(
    query: Optional[str] = Query(None, description="Search query for dimensions"),
    top_k: int = Query(10, description="Number of results", ge=1, le=50)
):
    """
    List or search available dimensions.
    
    Examples:
        GET /dimensions - List all dimensions
        GET /dimensions?query=location&top_k=5 - Search for location dimensions
    """
    try:
        retriever = get_retriever()
        
        if query:
            results = retriever.retrieve_dimensions(query, top_k=top_k)
        else:
            results = [r for r in retriever.metadata if r.get('type') == 'dimension'][:top_k]
            results = [RetrievalResult(
                type=r['type'],
                name=r['name'],
                description=r.get('description', ''),
                score=1.0,
                metadata=r
            ) for r in results]
        
        return {
            "query": query or "all",
            "count": len(results),
            "dimensions": [
                {
                    "name": r.name,
                    "description": r.description,
                    "sql_column": r.metadata.get('sql_column', ''),
                    "table": r.metadata.get('table', ''),
                    "possible_values": r.metadata.get('possible_values', []),
                    "score": r.score
                }
                for r in results
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dimensions error: {str(e)}")


def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the FastAPI server."""
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    print("=" * 70)
    print("Starting Ask Your Data - RAG API Server")
    print("=" * 70)
    print("Endpoints:")
    print("  GET  /              - Health check")
    print("  POST /retrieve      - Semantic search (JSON body)")
    print("  GET  /retrieve      - Semantic search (query params)")
    print("  GET  /context/{q}   - SQL generation context")
    print("  GET  /metrics       - List/search metrics")
    print("  GET  /dimensions    - List/search dimensions")
    print("  GET  /docs          - Interactive API docs")
    print("=" * 70)
    print()
    
    start_server()
