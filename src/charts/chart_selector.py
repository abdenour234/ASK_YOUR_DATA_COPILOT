"""
Chart Type Selector
Automatically selects appropriate chart type based on query intent and data structure
"""

from typing import Dict, List, Optional
import pandas as pd
from src.nlp.models import Intent


class ChartSelector:
    """Selects optimal chart type for query results."""
    
    def select_chart(self, intent: Intent, data: pd.DataFrame) -> Dict:
        """
        Select appropriate chart type and configuration.
        
        Args:
            intent: Parsed intent object
            data: Query result DataFrame
            
        Returns:
            Chart configuration dict with type, x, y, title, etc.
        """
        
        # Single value → Metric card
        if len(data) == 1 and len(data.columns) <= 2:
            return {
                'type': 'metric',
                'value': data.iloc[0, -1],
                'label': data.columns[-1].replace('_', ' ').title()
            }
        
        # Multiple metrics for same dimension → Grouped bar
        if len(data.columns) > 2:
            return self._build_multi_metric_config(intent, data)
        
        # Time series detection
        time_keywords = ['month', 'year', 'date', 'day', 'week', 'quarter']
        first_col = data.columns[0].lower()
        is_time_series = any(keyword in first_col for keyword in time_keywords)
        
        # Percentage/proportion detection → Pie chart
        if self._is_percentage_data(data):
            return self._build_pie_config(intent, data)
        
        # Geographic data detection
        geo_keywords = ['state', 'city', 'country', 'region', 'zip']
        has_geo = any(keyword in first_col for keyword in geo_keywords)
        
        # Distribution detection → Box plot or Histogram
        if self._is_distribution_query(intent, data):
            return self._build_distribution_config(intent, data)
        
        # Scatter plot for correlation queries
        if len(data.columns) >= 3 and self._is_correlation_query(intent):
            return self._build_scatter_config(intent, data)
        
        # Chart type selection based on intent
        if is_time_series:
            if len(data) > 20:
                chart_type = 'area'  # Better for long time series
            else:
                chart_type = 'line'
        elif intent.intent_type == 'top_n':
            if len(data) <= 10:
                chart_type = 'bar'
            else:
                chart_type = 'treemap'  # Better for many items
        elif intent.intent_type == 'comparison':
            chart_type = 'grouped_bar'
        else:
            chart_type = 'bar'
        
        # Build config
        config = {
            'type': chart_type,
            'data': data,
            'x': data.columns[0],
            'y': data.columns[1] if len(data.columns) > 1 else data.columns[0],
            'title': self._generate_chart_title(intent, data),
            'x_label': data.columns[0].replace('_', ' ').title(),
            'y_label': data.columns[1].replace('_', ' ').title() if len(data.columns) > 1 else 'Value'
        }
        
        # Horizontal bars for long labels
        if chart_type == 'bar' and intent.intent_type == 'top_n':
            avg_label_length = data[data.columns[0]].astype(str).str.len().mean()
            config['orientation'] = 'h' if avg_label_length > 10 else 'v'
        
        return config
    
    def _is_percentage_data(self, data: pd.DataFrame) -> bool:
        """Check if data represents percentages/proportions."""
        if len(data) > 15:  # Too many categories for pie
            return False
        
        # Check if values sum to ~100 or ~1.0
        numeric_col = data.select_dtypes(include=['number']).columns
        if len(numeric_col) > 0:
            total = data[numeric_col[0]].sum()
            return 95 <= total <= 105 or 0.95 <= total <= 1.05
        return False
    
    def _is_distribution_query(self, intent: Intent, data: pd.DataFrame) -> bool:
        """Check if query is about distribution/statistics."""
        distribution_keywords = ['distribution', 'range', 'spread', 'variance', 'percentile']
        query_lower = ' '.join(intent.metrics + intent.dimensions).lower()
        return any(keyword in query_lower for keyword in distribution_keywords)
    
    def _is_correlation_query(self, intent: Intent) -> bool:
        """Check if query is about correlation between variables."""
        correlation_keywords = ['correlation', 'relationship', 'vs', 'versus', 'compare']
        query_text = ' '.join(intent.metrics + intent.dimensions).lower()
        return any(keyword in query_text for keyword in correlation_keywords)
    
    def _build_pie_config(self, intent: Intent, data: pd.DataFrame) -> Dict:
        """Build pie chart configuration."""
        return {
            'type': 'pie',
            'data': data,
            'labels': data.columns[0],
            'values': data.columns[1],
            'title': self._generate_chart_title(intent, data)
        }
    
    def _build_multi_metric_config(self, intent: Intent, data: pd.DataFrame) -> Dict:
        """Build grouped bar chart for multiple metrics."""
        return {
            'type': 'grouped_bar',
            'data': data,
            'x': data.columns[0],
            'y_columns': list(data.columns[1:]),
            'title': self._generate_chart_title(intent, data),
            'x_label': data.columns[0].replace('_', ' ').title()
        }
    
    def _build_scatter_config(self, intent: Intent, data: pd.DataFrame) -> Dict:
        """Build scatter plot configuration."""
        return {
            'type': 'scatter',
            'data': data,
            'x': data.columns[0],
            'y': data.columns[1],
            'size': data.columns[2] if len(data.columns) > 2 else None,
            'title': f"{data.columns[1].replace('_', ' ').title()} vs {data.columns[0].replace('_', ' ').title()}",
            'x_label': data.columns[0].replace('_', ' ').title(),
            'y_label': data.columns[1].replace('_', ' ').title()
        }
    
    def _build_distribution_config(self, intent: Intent, data: pd.DataFrame) -> Dict:
        """Build box plot or histogram configuration."""
        if len(data) < 20:
            chart_type = 'box'
        else:
            chart_type = 'histogram'
        
        return {
            'type': chart_type,
            'data': data,
            'x': data.columns[0],
            'y': data.columns[1] if len(data.columns) > 1 else None,
            'title': self._generate_chart_title(intent, data)
        }
    
    def _generate_chart_title(self, intent: Intent, data: pd.DataFrame) -> str:
        """Generate descriptive chart title."""
        if intent.intent_type == 'top_n':
            metric = intent.metrics[0] if intent.metrics else data.columns[1]
            dimension = intent.dimensions[0] if intent.dimensions else data.columns[0]
            return f"Top {len(data)} {dimension.replace('_', ' ').title()} by {metric.replace('_', ' ').title()}"
        
        elif intent.intent_type == 'time_series':
            metric = intent.metrics[0] if intent.metrics else data.columns[1]
            return f"{metric.replace('_', ' ').title()} Over Time"
        
        elif intent.intent_type == 'comparison':
            return f"Comparison: {data.columns[1].replace('_', ' ').title()}"
        
        else:
            if len(data.columns) > 1:
                return f"{data.columns[1].replace('_', ' ').title()} by {data.columns[0].replace('_', ' ').title()}"
            else:
                return f"{data.columns[0].replace('_', ' ').title()} Distribution"
