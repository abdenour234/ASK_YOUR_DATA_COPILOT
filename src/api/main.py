"""
Simple FastAPI app for RAG endpoint
"""

from fastapi import FastAPI
from typing import List, Dict
from src.api.rag import search_glossary

app = FastAPI(title="Ask Your Data API")


@app.get("/")
def root():
    """Health check."""
    return {"status": "ok", "message": "Ask Your Data API"}


@app.post("/search")
def search(query: str, top_k: int = 5) -> Dict:
    """
    Search glossary for relevant context.
    
    Args:
        query: Natural language query
        top_k: Number of results to return
    
    Returns:
        Dict with query and results list
    """
    results = search_glossary(query, top_k)
    return {
        "query": query,
        "top_k": top_k,
        "results": results
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
