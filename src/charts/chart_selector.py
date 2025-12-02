"""
Simple chart selector - chooses chart type based on data
"""

import pandas as pd
from typing import Dict


def choose_chart(intent: Dict, data: pd.DataFrame) -> Dict:
    """
    Select chart type and config.
    
    Returns dict with:
    - type: chart type ('bar', 'line', 'metric', 'pie', etc.)
    - x: x-axis column
    - y: y-axis column
    - title: chart title
    """
    if data.empty:
        return {'type': 'empty'}
    
    # Single value -> metric card
    if len(data) == 1 and len(data.columns) <= 2:
        return {
            'type': 'metric',
            'value': data.iloc[0, -1],
            'label': data.columns[-1].replace('_', ' ').title()
        }
    
    # Time series detection
    first_col = data.columns[0].lower()
    is_time = any(word in first_col for word in ['month', 'year', 'date', 'day'])
    
    # Choose chart type
    intent_type = intent.get('intent_type', 'group_by')
    
    if is_time:
        chart_type = 'line'
    elif intent_type == 'top_n':
        chart_type = 'bar'
    else:
        chart_type = 'bar'
    
    # Get column names
    x_col = data.columns[0]
    y_col = data.columns[1] if len(data.columns) > 1 else data.columns[0]
    
    return {
        'type': chart_type,
        'data': data,
        'x': x_col,
        'y': y_col,
        'title': intent.get('original_query', 'Query Results'),
        'x_label': x_col.replace('_', ' ').title(),
        'y_label': y_col.replace('_', ' ').title()
    }
