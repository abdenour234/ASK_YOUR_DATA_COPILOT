"""
Simple intent parser - converts natural language to structured intent dict
"""

import os
import json
import requests
import re
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()


def call_llm(prompt: str, api_key: str = None, model: str = None) -> str:
    """Call LLM API and return response text."""
    api_key = api_key or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set")
    
    model = model or os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost:8501"),
        "X-Title": os.getenv("OPENROUTER_SITE_NAME", "Ask Your Data")
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=30
    )
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']


def extract_json(text: str) -> Dict:
    """Extract JSON from LLM response."""
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    return json.loads(text)


def build_prompt(query: str, rag_context: Optional[Dict] = None) -> str:
    """Build prompt for intent parsing."""
    prompt = f"""Parse this natural language query into structured JSON.

QUERY: "{query}\""""
    
    # Add RAG context if available
    if rag_context and rag_context.get('results'):
        prompt += "\n\nAVAILABLE CONTEXT FROM GLOSSARY:"
        for item in rag_context['results'][:5]:
            prompt += f"\n- {item.get('name')}: {item.get('description')}"
    
    prompt += """

Return JSON with these fields:
- intent_type: "top_n", "group_by", "filter", "time_series", "aggregation", "distribution"
- metrics: list of metrics to calculate (e.g., ["revenue", "order_count"])
- dimensions: list of dimensions to group by (e.g., ["customer_state"])
- filters: list of filter dicts with dimension, operator, value
- order_by: sort spec like "revenue DESC"
- limit: number for top_n queries
- confidence: float 0-1

Example output:
{{"intent_type": "top_n", "metrics": ["revenue"], "dimensions": ["customer_state"], "filters": [], "order_by": "revenue DESC", "limit": 10, "confidence": 0.95}}

Return ONLY valid JSON, no explanation."""
    
    return prompt


def parse_query(query: str, use_rag: bool = True) -> Dict:
    """
    Parse natural language query into intent dict.
    
    Returns dict with:
    - success: bool
    - intent: dict with intent_type, metrics, dimensions, etc.
    - error: str if failed
    """
    try:
        # Get RAG context if enabled
        rag_context = None
        if use_rag:
            try:
                from src.api.rag import search_glossary
                results = search_glossary(query, top_k=5)
                if results:
                    rag_context = {'results': results}
            except:
                pass
        
        prompt = build_prompt(query, rag_context)
        response = call_llm(prompt)
        intent = extract_json(response)
        
        intent['original_query'] = query
        
        return {
            'success': True,
            'intent': intent,
            'error': None
        }
    except Exception as e:
        return {
            'success': False,
            'intent': None,
            'error': str(e)
        }
