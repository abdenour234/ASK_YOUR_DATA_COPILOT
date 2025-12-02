"""
Ask Your Data - Simple Streamlit Interface
Natural language to SQL query interface - simplified with no OOP
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from src.nlp.intent_parser import parse_query
from src.sql.generator import generate_sql
from src.sql.executor import connect_db, run_query
from src.charts.chart_selector import choose_chart


# ============================================================================
# PAGE SETUP
# ============================================================================

st.set_page_config(
    page_title="Ask Your Data",
    page_icon="🔍",
    layout="wide"
)


# ============================================================================
# SIMPLE CSS
# ============================================================================

st.markdown("""
<style>
    .main { padding: 2rem; }
    .stButton>button { width: 100%; }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# INIT
# ============================================================================

def init():
    """Initialize app state and database."""
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    try:
        connect_db()
    except Exception as e:
        st.error(f"Database error: {e}")


# ============================================================================
# CHART RENDERING
# ============================================================================

def render_chart(config: dict, data: pd.DataFrame):
    """Render chart based on config."""
    chart_type = config.get('type')
    
    if chart_type == 'metric':
        value = config.get('value', 0)
        label = config.get('label', 'Value')
        try:
            st.metric(label, f"{float(value):,.2f}")
        except (ValueError, TypeError):
            st.metric(label, str(value))
        return
    
    if chart_type == 'empty' or data.empty:
        st.info("No data to display")
        return
    
    # Get chart params
    x = config.get('x')
    y = config.get('y')
    title = config.get('title', '')
    
    # Render chart
    try:
        if chart_type == 'line':
            fig = px.line(data, x=x, y=y, title=title)
        elif chart_type == 'bar':
            fig = px.bar(data, x=x, y=y, title=title)
        elif chart_type == 'pie':
            fig = px.pie(data, names=x, values=y, title=title)
        else:
            fig = px.bar(data, x=x, y=y, title=title)
        
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Chart rendering error: {e}")
        st.info("Showing data table instead")


# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main application."""
    init()
    
    # Header
    st.title("🔍 Ask Your Data")
    st.markdown("Natural language to SQL query interface")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 💡 Examples")
        examples = [
            "Top 10 states by revenue",
            "Total revenue by month",
            "Delivered orders in SP",
            "Top product categories"
        ]
        for ex in examples:
            if st.button(ex, key=ex):
                st.session_state.query = ex
        
        st.markdown("---")
        
        # History
        if st.session_state.history:
            st.markdown("### 📜 Recent Queries")
            for i, item in enumerate(reversed(st.session_state.history[-5:])):
                st.caption(f"{item['query'][:40]}...")
    
    # Main input
    query = st.text_area(
        "Enter your question",
        placeholder="e.g., What are the top 10 customer states by revenue?",
        height=100,
        value=st.session_state.get('query', '')
    )
    
    if 'query' in st.session_state:
        del st.session_state.query
    
    col1, col2 = st.columns([1, 5])
    with col1:
        run_btn = st.button("🚀 Run", type="primary")
    with col2:
        clear_btn = st.button("🗑️ Clear")
    
    if clear_btn:
        st.rerun()
    
    # Process query
    if run_btn and query.strip():
        with st.spinner("Processing..."):
            # Step 1: Parse intent
            intent_result = parse_query(query)
            
            if not intent_result['success']:
                st.error(f"❌ Error: {intent_result['error']}")
                return
            
            intent = intent_result['intent']
            
            # Show intent
            with st.expander("📋 Parsed Intent", expanded=False):
                st.json(intent)
            
            # Step 2: Generate SQL
            sql_result = generate_sql(intent)
            
            if not sql_result['is_valid']:
                st.error(f"❌ Invalid SQL: {', '.join(sql_result['errors'])}")
                return
            
            sql = sql_result['sql']
            
            # Show SQL
            with st.expander("💻 Generated SQL", expanded=True):
                st.code(sql, language='sql')
            
            # Step 3: Execute query
            exec_result = run_query(sql)
            
            if not exec_result['success']:
                st.error(f"❌ Query failed: {exec_result['error']}")
                return
            
            data = exec_result['data']
            
            # Step 4: Display results
            st.markdown("### 📊 Results")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Rows", exec_result['row_count'])
            with col_b:
                st.metric("Execution Time", f"{exec_result['execution_time_ms']:.0f}ms")
            with col_c:
                st.metric("Columns", len(data.columns))
            
            # Data table
            st.dataframe(data, use_container_width=True)
            
            # Chart
            if not data.empty:
                st.markdown("### 📈 Visualization")
                chart_config = choose_chart(intent, data)
                render_chart(chart_config, data)
            
            # Add to history
            st.session_state.history.append({
                'query': query,
                'rows': exec_result['row_count'],
                'time': exec_result['execution_time_ms']
            })


if __name__ == "__main__":
    main()
