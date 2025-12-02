"""
Plotly Chart Renderer
Renders charts using Plotly Express
"""

import plotly.express as px
import plotly.graph_objects as go
from typing import Dict
import pandas as pd


class PlotlyRenderer:
    """Renders charts using Plotly."""
    
    def render(self, config: Dict) -> go.Figure:
        """
        Render chart based on configuration.
        
        Args:
            config: Chart configuration from ChartSelector
            
        Returns:
            Plotly Figure object or None for metric cards
        """
        chart_type = config['type']
        
        if chart_type == 'metric':
            return None  # Handled separately in Streamlit
        
        # Route to specific chart renderer
        renderers = {
            'bar': self._render_bar,
            'line': self._render_line,
            'area': self._render_area,
            'pie': self._render_pie,
            'grouped_bar': self._render_grouped_bar,
            'scatter': self._render_scatter,
            'box': self._render_box,
            'histogram': self._render_histogram,
            'treemap': self._render_treemap
        }
        
        renderer = renderers.get(chart_type, self._render_bar)
        return renderer(config)
    
    def _render_bar(self, config: Dict) -> go.Figure:
        """Render bar chart."""
        data = config['data']
        orientation = config.get('orientation', 'v')
        
        if orientation == 'h':
            # Horizontal bars
            fig = px.bar(
                data,
                x=config['y'],
                y=config['x'],
                orientation='h',
                title=config['title'],
                labels={config['y']: config['y_label'], config['x']: config['x_label']}
            )
            fig.update_yaxis(autorange="reversed")
        else:
            # Vertical bars
            fig = px.bar(
                data,
                x=config['x'],
                y=config['y'],
                title=config['title'],
                labels={config['x']: config['x_label'], config['y']: config['y_label']}
            )
        
        fig.update_traces(marker_color='#667eea')
        self._apply_common_styling(fig)
        return fig
    
    def _render_line(self, config: Dict) -> go.Figure:
        """Render line chart."""
        data = config['data']
        
        fig = px.line(
            data,
            x=config['x'],
            y=config['y'],
            title=config['title'],
            labels={config['x']: config['x_label'], config['y']: config['y_label']},
            markers=True
        )
        
        fig.update_traces(
            line_color='#667eea',
            line_width=3,
            marker=dict(size=8)
        )
        self._apply_common_styling(fig)
        return fig
    
    def _render_area(self, config: Dict) -> go.Figure:
        """Render area chart."""
        data = config['data']
        
        fig = px.area(
            data,
            x=config['x'],
            y=config['y'],
            title=config['title'],
            labels={config['x']: config['x_label'], config['y']: config['y_label']}
        )
        
        fig.update_traces(
            fillcolor='rgba(102, 126, 234, 0.3)',
            line_color='#667eea',
            line_width=2
        )
        self._apply_common_styling(fig)
        return fig
    
    def _render_pie(self, config: Dict) -> go.Figure:
        """Render pie/donut chart."""
        data = config['data']
        
        fig = px.pie(
            data,
            names=config['labels'],
            values=config['values'],
            title=config['title'],
            hole=0.3  # Donut chart
        )
        
        fig.update_traces(
            marker=dict(colors=px.colors.sequential.Purples_r),
            textposition='inside',
            textinfo='percent+label'
        )
        self._apply_common_styling(fig)
        return fig
    
    def _render_grouped_bar(self, config: Dict) -> go.Figure:
        """Render grouped bar chart."""
        data = config['data']
        
        # Melt data for grouped bars
        melted = data.melt(
            id_vars=config['x'],
            value_vars=config['y_columns']
        )
        
        fig = px.bar(
            melted,
            x=config['x'],
            y='value',
            color='variable',
            title=config['title'],
            barmode='group',
            labels={'variable': 'Metric', 'value': 'Value', config['x']: config['x_label']}
        )
        
        fig.update_traces(marker_line_width=0)
        self._apply_common_styling(fig)
        return fig
    
    def _render_scatter(self, config: Dict) -> go.Figure:
        """Render scatter plot."""
        data = config['data']
        
        fig = px.scatter(
            data,
            x=config['x'],
            y=config['y'],
            size=config.get('size'),
            title=config['title'],
            labels={config['x']: config['x_label'], config['y']: config['y_label']},
            trendline='ols'  # Add trend line
        )
        
        fig.update_traces(
            marker=dict(color='#667eea', size=10, opacity=0.7)
        )
        self._apply_common_styling(fig)
        return fig
    
    def _render_box(self, config: Dict) -> go.Figure:
        """Render box plot."""
        data = config['data']
        
        fig = px.box(
            data,
            x=config['x'],
            y=config.get('y'),
            title=config['title']
        )
        
        fig.update_traces(marker_color='#667eea', fillcolor='rgba(102, 126, 234, 0.5)')
        self._apply_common_styling(fig)
        return fig
    
    def _render_histogram(self, config: Dict) -> go.Figure:
        """Render histogram."""
        data = config['data']
        
        fig = px.histogram(
            data,
            x=config['x'],
            title=config['title'],
            nbins=30
        )
        
        fig.update_traces(marker_color='#667eea')
        self._apply_common_styling(fig)
        return fig
    
    def _render_treemap(self, config: Dict) -> go.Figure:
        """Render treemap for hierarchical data."""
        data = config['data']
        
        fig = px.treemap(
            data,
            path=[config['x']],
            values=config['y'],
            title=config['title'],
            color=config['y'],
            color_continuous_scale='Purples'
        )
        
        fig.update_traces(textinfo='label+value+percent parent')
        self._apply_common_styling(fig)
        return fig
    
    def _apply_common_styling(self, fig: go.Figure):
        """Apply common styling to all charts."""
        fig.update_layout(
            template='plotly_white',
            hovermode='x unified',
            title_font_size=18,
            title_font_family='Inter',
            height=450,
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
