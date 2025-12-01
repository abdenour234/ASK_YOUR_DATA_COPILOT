"""
Sprint 2 - Ticket 5: Intent Parser
Uses OpenRouter API (GPT-4) to parse natural language queries into structured Intent objects.

Dependencies: requests, python-dotenv, src.nlp.models
"""

import os
import json
import requests
import re
from typing import Dict, Optional
from dotenv import load_dotenv
from src.nlp.models import Intent, IntentParseResult
from src.api.rag import get_retriever

# Load environment variables
load_dotenv()


class IntentParser:
    """
    Parses natural language queries into structured Intent objects using OpenRouter API.
    
    Uses GPT-4 via OpenRouter to convert user queries like "top 10 products by revenue"
    into structured Intent objects with metrics, dimensions, filters, etc.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "openrouter/auto",
        site_url: Optional[str] = None,
        site_name: Optional[str] = None
    ):
        """
        Initialize Intent Parser.
        
        Args:
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var)
            model: Model to use (default: openrouter/auto - picks free model)
            site_url: Your site URL for OpenRouter rankings (optional)
            site_name: Your site name for OpenRouter rankings (optional)
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable "
                "or pass api_key parameter. Get your key from: https://openrouter.ai/keys"
            )
        
        self.model = model or os.getenv("OPENROUTER_MODEL", "openrouter/auto")
        self.site_url = site_url or os.getenv("OPENROUTER_SITE_URL", "http://localhost:8501")
        self.site_name = site_name or os.getenv("OPENROUTER_SITE_NAME", "Ask Your Data Copilot")
        
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Get RAG retriever for context enrichment
        try:
            self.retriever = get_retriever()
        except Exception as e:
            print(f"Warning: Could not initialize RAG retriever: {e}")
            self.retriever = None
    
    def parse(
        self, 
        query: str, 
        rag_context: Optional[Dict] = None,
        use_rag: bool = True
    ) -> IntentParseResult:
        """
        Parse natural language query into structured Intent.
        
        Args:
            query: Natural language query from user
            rag_context: Optional pre-fetched RAG context (if None, will fetch automatically)
            use_rag: Whether to use RAG context enrichment (default: True)
        
        Returns:
            IntentParseResult with success status and Intent object (if successful)
        
        Example:
            >>> parser = IntentParser()
            >>> result = parser.parse("What are the top 10 product categories by revenue?")
            >>> if result.success:
            >>>     print(result.intent.intent_type)  # 'top_n'
            >>>     print(result.intent.metrics)      # ['revenue']
            >>>     print(result.intent.dimensions)   # ['product_category']
        """
        try:
            # Get RAG context if not provided
            if use_rag and rag_context is None and self.retriever:
                try:
                    rag_context = self.retriever.get_context_for_sql(query, top_k=5)
                except Exception as e:
                    print(f"Warning: RAG context retrieval failed: {e}")
                    rag_context = None
            
            # Build prompt
            prompt = self._build_prompt(query, rag_context)
            
            # Call OpenRouter API
            response = self._call_openrouter(prompt)
            
            # Extract and parse JSON
            intent_json = self._extract_json(response)
            
            # Add original query
            intent_json['original_query'] = query
            
            # Create Intent object
            intent = Intent(**intent_json)
            
            return IntentParseResult(
                success=True,
                intent=intent,
                error=None,
                raw_response=response
            )
        
        except Exception as e:
            return IntentParseResult(
                success=False,
                intent=None,
                error=str(e),
                raw_response=None
            )
    
    def _build_prompt(self, query: str, rag_context: Optional[Dict]) -> str:
        """Build prompt for OpenRouter API."""
        
        prompt = f"""You are an expert SQL query intent parser for an e-commerce analytics system.

USER QUERY: "{query}"
"""
        
        # Add RAG context if available
        if rag_context:
            prompt += f"""
AVAILABLE CONTEXT FROM KNOWLEDGE BASE:

Metrics (what to measure):
{self._format_metrics(rag_context.get('metrics', []))}

Dimensions (how to group/filter):
{self._format_dimensions(rag_context.get('dimensions', []))}
"""
            
            if rag_context.get('common_patterns'):
                prompt += f"""
Similar Query Patterns Found:
{self._format_patterns(rag_context['common_patterns'])}
"""
        
        prompt += """
TASK: Extract structured intent from the user query.

Determine:
1. **intent_type**: Choose from:
   - "top_n": Top/bottom N items (e.g., "top 10 products")
   - "group_by": Group by analysis (e.g., "revenue by state")
   - "filter": Simple filter query (e.g., "orders from SP")
   - "time_series": Temporal analysis (e.g., "monthly sales trend")
   - "comparison": Compare groups (e.g., "compare Q1 vs Q2")
   - "aggregation": Single aggregation (e.g., "what is total revenue?")
   - "distribution": Distribution analysis (e.g., "payment method breakdown")
   - "ranking": Rank items (e.g., "rank states by revenue")

2. **metrics**: Array of metric names to calculate (e.g., ["revenue", "order_count"])
   - Use ONLY metric names from the context above
   - If no metrics provided but needed, infer from query (e.g., "top products" implies revenue or count)

3. **dimensions**: Array of dimension names to group by or filter on
   - Use ONLY dimension names from the context above

4. **filters**: Array of filter objects with structure:
   ```json
   {"dimension": "order_status", "operator": "=", "value": "delivered"}
   ```
   - Operators: =, !=, >, <, >=, <=, IN, NOT IN, LIKE, BETWEEN

5. **date_range**: If query mentions dates/time periods:
   ```json
   {"start_date": "2017-01-01", "end_date": "2017-12-31"}
   ```

6. **order_by**: Sort specification (e.g., "revenue DESC", "customer_state ASC")
   - For top_n queries, typically sort by the metric DESC
   - For time_series, typically sort by time dimension ASC

7. **limit**: Number of results (for top_n queries, extract from "top 10", "bottom 5", etc.)

8. **time_grain**: For time_series queries, choose from: "day", "week", "month", "quarter", "year"

9. **confidence**: Float 0-1 indicating how confident you are in this parsing
   - 0.9-1.0: Very clear, unambiguous query
   - 0.7-0.9: Clear query with minor ambiguity
   - 0.5-0.7: Somewhat ambiguous, made reasonable assumptions
   - <0.5: Very ambiguous, low confidence

IMPORTANT RULES:
- Use ONLY metric and dimension names from the context provided
- If a metric/dimension isn't in the context, use your best judgment but lower confidence
- For "top N" queries: intent_type="top_n", order_by="<metric> DESC", limit=N
- For "by <dimension>" queries: intent_type="group_by", dimensions=[<dimension>]
- For "what is total..." queries: intent_type="aggregation", dimensions=[]
- Always include confidence score

Respond ONLY with valid JSON matching this exact structure (no explanations, no markdown):
{
  "intent_type": "top_n",
  "metrics": ["revenue"],
  "dimensions": ["product_category"],
  "filters": [],
  "date_range": null,
  "order_by": "revenue DESC",
  "limit": 10,
  "time_grain": null,
  "comparison_dimension": null,
  "confidence": 0.95
}
"""
        
        return prompt
    
    def _format_metrics(self, metrics: list) -> str:
        """Format metrics for prompt."""
        if not metrics:
            return "  (No specific metrics found in context)"
        
        lines = []
        for m in metrics:
            lines.append(f"  - {m['name']}: {m['description']}")
            lines.append(f"    SQL: {m.get('aggregation', 'SUM')}({m['sql_column']}) from {m['table']}")
        return "\n".join(lines)
    
    def _format_dimensions(self, dimensions: list) -> str:
        """Format dimensions for prompt."""
        if not dimensions:
            return "  (No specific dimensions found in context)"
        
        lines = []
        for d in dimensions:
            lines.append(f"  - {d['name']}: {d['description']}")
            lines.append(f"    SQL: {d['sql_column']} from {d['table']}")
        return "\n".join(lines)
    
    def _format_patterns(self, patterns: list) -> str:
        """Format common patterns for prompt."""
        if not patterns:
            return "  (No similar patterns found)"
        
        lines = []
        for p in patterns:
            lines.append(f"  - \"{p['query']}\" (intent: {p['intent']})")
            sql_pattern = p.get('sql_pattern', '')
            if sql_pattern:
                # Truncate long patterns
                if len(sql_pattern) > 100:
                    sql_pattern = sql_pattern[:100] + "..."
                lines.append(f"    Pattern: {sql_pattern}")
        return "\n".join(lines)
    
    def _call_openrouter(self, prompt: str) -> str:
        """Call OpenRouter API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": self.site_url,
            "X-Title": self.site_name,
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert at parsing natural language queries into structured JSON. You always respond with valid JSON and nothing else."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,  # Low temperature for consistency
            "max_tokens": 1000
        }
        
        response = requests.post(
            self.api_url,
            headers=headers,
            data=json.dumps(data),
            timeout=30
        )
        
        response.raise_for_status()
        
        result = response.json()
        
        # Extract content from OpenRouter response
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        else:
            raise ValueError(f"Unexpected API response format: {result}")
    
    def _extract_json(self, response_text: str) -> Dict:
        """Extract JSON from LLM response."""
        # Remove markdown code blocks if present
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        
        # Try to find JSON object in response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in response: {e}\nResponse: {response_text}")
        else:
            raise ValueError(f"No JSON found in response: {response_text}")


# Convenience function
def parse_intent(query: str, use_rag: bool = True) -> IntentParseResult:
    """
    Parse a natural language query into structured Intent.
    
    Args:
        query: Natural language query
        use_rag: Whether to use RAG context (default: True)
    
    Returns:
        IntentParseResult with Intent object
    
    Example:
        >>> from src.nlp.intent_parser import parse_intent
        >>> result = parse_intent("Show me the top 10 product categories by revenue")
        >>> if result.success:
        >>>     print(f"Intent type: {result.intent.intent_type}")
        >>>     print(f"Metrics: {result.intent.metrics}")
    """
    parser = IntentParser()
    return parser.parse(query, use_rag=use_rag)
