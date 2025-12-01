"""
Reusable UI Components for Ask Your Data Copilot
Sprint 2, Ticket 8: Component Library
"""

import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any, List


def render_stat_card(label: str, value: str, icon: str = "📊", color: str = "#667eea"):
    """
    Render a professional statistic card.
    
    Args:
        label: Card label
        value: Card value
        icon: Emoji icon
        color: Border color (hex)
    """
    st.markdown(f"""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
            border-left: 4px solid {color};
        ">
            <div style="
                font-size: 0.85rem;
                font-weight: 600;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 0.5rem;
            ">{icon} {label}</div>
            <div style="
                font-size: 2rem;
                font-weight: 700;
                color: #1e293b;
            ">{value}</div>
        </div>
    """, unsafe_allow_html=True)


def render_info_box(title: str, content: str, type: str = "info"):
    """
    Render an information box.
    
    Args:
        title: Box title
        content: Box content
        type: 'info', 'success', 'warning', 'error'
    """
    colors = {
        'info': {'bg': '#eff6ff', 'border': '#3b82f6', 'icon': 'ℹ️'},
        'success': {'bg': '#dcfce7', 'border': '#22c55e', 'icon': '✅'},
        'warning': {'bg': '#fef3c7', 'border': '#f59e0b', 'icon': '⚠️'},
        'error': {'bg': '#fee2e2', 'border': '#ef4444', 'icon': '❌'}
    }
    
    style = colors.get(type, colors['info'])
    
    st.markdown(f"""
        <div style="
            background: {style['bg']};
            padding: 1rem 1.5rem;
            border-radius: 8px;
            border-left: 4px solid {style['border']};
            margin: 1rem 0;
        ">
            <div style="font-weight: 600; margin-bottom: 0.5rem;">
                {style['icon']} {title}
            </div>
            <div style="color: #334155;">
                {content}
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_section_header(text: str, icon: str = ""):
    """Render a section header."""
    st.markdown(f"""
        <div style="
            font-size: 1.5rem;
            font-weight: 700;
            color: #1e293b;
            margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid #667eea;
            display: inline-block;
        ">
            {icon} {text}
        </div>
    """, unsafe_allow_html=True)


def render_badge(text: str, color: str = "#667eea"):
    """Render a badge/pill."""
    st.markdown(f"""
        <span style="
            background: {color};
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
            margin: 0.25rem;
        ">{text}</span>
    """, unsafe_allow_html=True)


def render_timeline_item(title: str, description: str, time: str, status: str = "completed"):
    """
    Render a timeline item for query history.
    
    Args:
        title: Event title
        description: Event description
        time: Time/date string
        status: 'completed', 'processing', 'failed'
    """
    status_colors = {
        'completed': '#22c55e',
        'processing': '#f59e0b',
        'failed': '#ef4444'
    }
    
    color = status_colors.get(status, '#64748b')
    
    st.markdown(f"""
        <div style="
            border-left: 3px solid {color};
            padding-left: 1.5rem;
            margin-bottom: 1.5rem;
            position: relative;
        ">
            <div style="
                position: absolute;
                left: -0.6rem;
                top: 0.2rem;
                width: 1rem;
                height: 1rem;
                background: {color};
                border-radius: 50%;
                border: 3px solid white;
            "></div>
            <div style="font-weight: 600; color: #1e293b; margin-bottom: 0.25rem;">
                {title}
            </div>
            <div style="color: #64748b; font-size: 0.9rem; margin-bottom: 0.25rem;">
                {description}
            </div>
            <div style="color: #94a3b8; font-size: 0.8rem;">
                {time}
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_data_preview(data: pd.DataFrame, max_rows: int = 5):
    """
    Render a styled data preview table.
    
    Args:
        data: DataFrame to display
        max_rows: Maximum rows to show
    """
    st.markdown("""
        <style>
        .dataframe-container {
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.dataframe(
        data.head(max_rows),
        use_container_width=True,
        height=min(300, (max_rows + 1) * 35 + 3)
    )
    
    if len(data) > max_rows:
        st.caption(f"Showing {max_rows} of {len(data):,} rows")


def render_loading_animation(message: str = "Processing..."):
    """Render a loading animation with message."""
    st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        ">
            <div style="
                font-size: 1.2rem;
                font-weight: 600;
                color: #667eea;
            ">
                ⏳ {message}
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_empty_state(icon: str, title: str, description: str):
    """Render an empty state placeholder."""
    st.markdown(f"""
        <div style="
            text-align: center;
            padding: 4rem 2rem;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
        ">
            <div style="font-size: 4rem; margin-bottom: 1rem;">
                {icon}
            </div>
            <div style="
                font-size: 1.5rem;
                font-weight: 700;
                color: #1e293b;
                margin-bottom: 0.5rem;
            ">
                {title}
            </div>
            <div style="color: #64748b; font-size: 1rem;">
                {description}
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_key_value_pair(key: str, value: str, inline: bool = False):
    """Render a key-value pair with styling."""
    if inline:
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #e2e8f0;">
                <span style="font-weight: 600; color: #64748b;">{key}:</span>
                <span style="color: #1e293b;">{value}</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style="margin-bottom: 1rem;">
                <div style="
                    font-size: 0.85rem;
                    font-weight: 600;
                    color: #64748b;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    margin-bottom: 0.25rem;
                ">{key}</div>
                <div style="
                    font-size: 1.1rem;
                    font-weight: 500;
                    color: #1e293b;
                ">{value}</div>
            </div>
        """, unsafe_allow_html=True)


def render_progress_steps(steps: List[Dict[str, Any]], current_step: int):
    """
    Render a progress indicator with steps.
    
    Args:
        steps: List of step dicts with 'title' and 'icon'
        current_step: Current step index (0-based)
    """
    num_steps = len(steps)
    
    html = '<div style="display: flex; justify-content: space-between; margin: 2rem 0;">'
    
    for i, step in enumerate(steps):
        is_completed = i < current_step
        is_current = i == current_step
        
        if is_completed:
            bg_color = '#22c55e'
            text_color = 'white'
        elif is_current:
            bg_color = '#667eea'
            text_color = 'white'
        else:
            bg_color = '#e2e8f0'
            text_color = '#94a3b8'
        
        html += f"""
            <div style="flex: 1; text-align: center;">
                <div style="
                    width: 3rem;
                    height: 3rem;
                    background: {bg_color};
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 0.5rem auto;
                    font-size: 1.5rem;
                    color: {text_color};
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                ">
                    {step['icon']}
                </div>
                <div style="
                    font-size: 0.85rem;
                    font-weight: 600;
                    color: {'#1e293b' if is_current or is_completed else '#94a3b8'};
                ">
                    {step['title']}
                </div>
            </div>
        """
        
        # Add connector line
        if i < num_steps - 1:
            line_color = '#22c55e' if i < current_step else '#e2e8f0'
            html += f"""
                <div style="
                    flex: 0 0 2rem;
                    height: 3px;
                    background: {line_color};
                    margin-top: 1.5rem;
                "></div>
            """
    
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_metric_comparison(metrics: List[Dict[str, Any]]):
    """
    Render a comparison of multiple metrics.
    
    Args:
        metrics: List of metric dicts with 'label', 'value', 'change', 'color'
    """
    cols = st.columns(len(metrics))
    
    for i, metric in enumerate(metrics):
        with cols[i]:
            change_color = '#22c55e' if metric.get('change', 0) >= 0 else '#ef4444'
            change_icon = '↗' if metric.get('change', 0) >= 0 else '↘'
            
            st.markdown(f"""
                <div style="
                    background: white;
                    padding: 1.5rem;
                    border-radius: 12px;
                    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
                    text-align: center;
                ">
                    <div style="
                        font-size: 0.85rem;
                        font-weight: 600;
                        color: #64748b;
                        text-transform: uppercase;
                        margin-bottom: 0.5rem;
                    ">{metric['label']}</div>
                    <div style="
                        font-size: 2rem;
                        font-weight: 700;
                        color: {metric.get('color', '#1e293b')};
                        margin-bottom: 0.5rem;
                    ">{metric['value']}</div>
                    <div style="
                        font-size: 0.9rem;
                        font-weight: 600;
                        color: {change_color};
                    ">
                        {change_icon} {metric.get('change', 0):+.1f}%
                    </div>
                </div>
            """, unsafe_allow_html=True)
