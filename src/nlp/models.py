"""
Sprint 2 - Ticket 5: Intent Models
Pydantic models for representing structured intents from natural language queries.

Dependencies: Pydantic
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import date


class Filter(BaseModel):
    """Represents a filter condition in a query."""
    dimension: str = Field(..., description="Dimension to filter on (e.g., 'order_status')")
    operator: Literal["=", "!=", ">", "<", ">=", "<=", "IN", "NOT IN", "LIKE", "BETWEEN"] = Field(
        ..., 
        description="Comparison operator"
    )
    value: str | int | float | List[str] | List[int] | List[float] = Field(
        ..., 
        description="Value(s) to compare against"
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "dimension": "order_status",
                    "operator": "=",
                    "value": "delivered"
                },
                {
                    "dimension": "customer_state",
                    "operator": "IN",
                    "value": ["SP", "RJ", "MG"]
                },
                {
                    "dimension": "revenue",
                    "operator": ">",
                    "value": 1000
                }
            ]
        }


class DateRange(BaseModel):
    """Represents a date range filter."""
    start_date: Optional[date] = Field(None, description="Start date (inclusive)")
    end_date: Optional[date] = Field(None, description="End date (inclusive)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2017-01-01",
                "end_date": "2017-12-31"
            }
        }


class Intent(BaseModel):
    """
    Structured representation of user intent extracted from natural language query.
    
    This is the core data structure that bridges natural language and SQL generation.
    """
    
    # Intent classification
    intent_type: Literal[
        "top_n",           # Top/bottom N items (e.g., "top 10 products")
        "group_by",        # Group by analysis (e.g., "revenue by state")
        "filter",          # Simple filter query (e.g., "orders from SP")
        "time_series",     # Temporal analysis (e.g., "monthly sales trend")
        "comparison",      # Compare groups (e.g., "compare Q1 vs Q2")
        "aggregation",     # Single aggregation (e.g., "what is total revenue?")
        "distribution",    # Distribution analysis (e.g., "payment method breakdown")
        "ranking"          # Rank items (e.g., "rank states by revenue")
    ] = Field(
        ..., 
        description="Type of analysis requested"
    )
    
    # What to measure
    metrics: List[str] = Field(
        default_factory=list,
        description="Metrics to calculate (e.g., ['revenue', 'order_count'])"
    )
    
    # How to group/slice
    dimensions: List[str] = Field(
        default_factory=list,
        description="Dimensions to group by or filter on (e.g., ['product_category', 'customer_state'])"
    )
    
    # Filters
    filters: List[Filter] = Field(
        default_factory=list,
        description="Filter conditions to apply"
    )
    
    # Date range filter (common enough to separate)
    date_range: Optional[DateRange] = Field(
        None,
        description="Date range filter (if temporal query)"
    )
    
    # Sorting
    order_by: Optional[str] = Field(
        None,
        description="Sort specification (e.g., 'revenue DESC', 'customer_state ASC')"
    )
    
    # Limit
    limit: Optional[int] = Field(
        None,
        description="Number of results to return (for top_n queries)",
        ge=1,
        le=1000
    )
    
    # Temporal granularity
    time_grain: Optional[Literal["day", "week", "month", "quarter", "year"]] = Field(
        None,
        description="Time granularity for time_series queries"
    )
    
    # Comparison parameters
    comparison_dimension: Optional[str] = Field(
        None,
        description="Dimension for comparison queries (e.g., 'year' for year-over-year)"
    )
    
    # Confidence score
    confidence: float = Field(
        ...,
        description="Confidence score (0-1) indicating how certain the parser is",
        ge=0.0,
        le=1.0
    )
    
    # Original query for reference
    original_query: str = Field(
        ...,
        description="Original natural language query from user"
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "intent_type": "top_n",
                    "metrics": ["revenue"],
                    "dimensions": ["product_category"],
                    "filters": [],
                    "date_range": None,
                    "order_by": "revenue DESC",
                    "limit": 10,
                    "time_grain": None,
                    "comparison_dimension": None,
                    "confidence": 0.95,
                    "original_query": "What are the top 10 product categories by revenue?"
                },
                {
                    "intent_type": "time_series",
                    "metrics": ["revenue", "order_count"],
                    "dimensions": ["month"],
                    "filters": [
                        {
                            "dimension": "order_status",
                            "operator": "=",
                            "value": "delivered"
                        }
                    ],
                    "date_range": {
                        "start_date": "2017-01-01",
                        "end_date": "2017-12-31"
                    },
                    "order_by": "month ASC",
                    "limit": None,
                    "time_grain": "month",
                    "comparison_dimension": None,
                    "confidence": 0.92,
                    "original_query": "Show me monthly revenue and order trends for 2017"
                },
                {
                    "intent_type": "aggregation",
                    "metrics": ["revenue"],
                    "dimensions": [],
                    "filters": [],
                    "date_range": None,
                    "order_by": None,
                    "limit": None,
                    "time_grain": None,
                    "comparison_dimension": None,
                    "confidence": 0.98,
                    "original_query": "What is the total revenue?"
                }
            ]
        }


class IntentParseResult(BaseModel):
    """Result of intent parsing operation."""
    success: bool
    intent: Optional[Intent] = None
    error: Optional[str] = None
    raw_response: Optional[str] = Field(None, description="Raw LLM response for debugging")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "intent": {
                    "intent_type": "top_n",
                    "metrics": ["revenue"],
                    "dimensions": ["product_category"],
                    "filters": [],
                    "order_by": "revenue DESC",
                    "limit": 10,
                    "confidence": 0.95,
                    "original_query": "top 10 categories"
                },
                "error": None,
                "raw_response": "{\"intent_type\": \"top_n\", ...}"
            }
        }
