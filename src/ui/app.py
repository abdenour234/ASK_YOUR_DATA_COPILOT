"""
Ask Your Data Copilot - Streamlit Interface
Natural Language to SQL Query Interface

Complete interface: Query → SQL → Results Table + Auto Visualization
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path
import os
import time

# Add project root to path - must be done before other imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.nlp.intent_parser import IntentParser
from src.sql.generator import SQLGenerator
from src.sql.executor import SQLExecutor
from src.nlp.models import Intent
from src.charts.chart_selector import ChartSelector
from src.charts.plotly_renderer import PlotlyRenderer


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Ask Your Data | SQL Query Interface",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Ask Your Data Copilot - Natural Language to SQL"
    }
)


# ============================================================================
# CUSTOM CSS STYLING
# ============================================================================

def load_custom_css():
    """Apply clean custom styling."""
    st.markdown("""
        <style>
        /* Import modern fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global styles */
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        /* Main container */
        .main {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 2rem;
        }
        
        /* Header styling */
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem 2.5rem;
            border-radius: 16px;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
        }
        
        .main-header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0;
            letter-spacing: -0.5px;
        }
        
        .main-header p {
            font-size: 1.1rem;
            margin: 0.5rem 0 0 0;
            opacity: 0.95;
            font-weight: 300;
        }
        
        /* Section headers */
        .section-header {
            font-size: 1.5rem;
            font-weight: 600;
            color: #2d3748;
            margin: 1.5rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid #667eea;
        }
        
        /* Metric display */
        .metric-box {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .metric-label {
            font-size: 0.875rem;
            font-weight: 500;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #667eea;
        }
        </style>
    """, unsafe_allow_html=True)


# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

def init_session_state():
    """Initialize session state variables."""
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []


# ============================================================================
# COMPONENT INITIALIZATION
# ============================================================================

@st.cache_resource
def initialize_components():
    """Initialize and cache application components."""
    try:
        parser = IntentParser()
        generator = SQLGenerator()
        executor = SQLExecutor()
        executor.connect()
        chart_selector = ChartSelector()
        chart_renderer = PlotlyRenderer()
        return parser, generator, executor, chart_selector, chart_renderer, None
    except Exception as e:
        return None, None, None, None, None, str(e)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point."""
    
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    init_session_state()
    
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>🔍 Ask Your Data Copilot</h1>
            <p>Natural Language → SQL Query → Data Table + Smart Visualization</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize components
    with st.spinner("🔧 Initializing AI components..."):
        parser, generator, executor, chart_selector, chart_renderer, init_error = initialize_components()
    
    if init_error:
        st.error(f"⚠️ Initialization Error: {init_error}")
        st.info("💡 Please check that your environment is properly configured and the database is accessible.")
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ System Status")
        
        # API Status
        with st.expander("🔌 API Configuration", expanded=False):
            api_key = os.getenv('OPENROUTER_API_KEY')
            if api_key:
                st.success("✅ OpenRouter API Connected")
                st.caption("Model: openai/gpt-4o")
            else:
                st.warning("⚠️ API Key Not Found")
                st.caption("Set OPENROUTER_API_KEY in .env")
        
        # Database Info
        with st.expander("💾 Database Status", expanded=False):
            try:
                result = executor.execute("SELECT COUNT(*) as total_orders FROM main_mart.fact_orders")
                if result.success:
                    total_orders = result.data['total_orders'].values[0]
                    st.success(f"✅ Connected to DuckDB")
                    st.metric("Total Orders", f"{total_orders:,}")
                else:
                    st.error("❌ Database Error")
            except Exception as e:
                st.error(f"❌ {str(e)[:50]}")
        
        st.markdown("---")
        
        # Query History
        st.markdown("### 📜 Recent Queries")
        if st.session_state.query_history:
            for i, item in enumerate(reversed(st.session_state.query_history[-5:])):
                with st.expander(f"Query {len(st.session_state.query_history) - i}", expanded=False):
                    st.caption(item['query'])
                    st.caption(f"⏱️ {item['execution_time']:.0f}ms")
                    st.caption(f"📊 {item['rows']} rows")
        else:
            st.caption("No queries yet")
        
        st.markdown("---")
        
        # Example Queries
        st.markdown("### 💡 Example Queries")
        examples = [
            "Top 10 states by revenue",
            "Total revenue by region",
            "Monthly revenue for 2017",
            "Delivered orders in SP",
            "Top product categories",
            "Weekend vs weekday orders"
        ]
        for example in examples:
            if st.button(example, key=f"ex_{example}", use_container_width=True):
                st.session_state.example_query = example
        
        st.markdown("---")
        st.caption("Ask Your Data Copilot v3.0.0")
    
    # Main content
    st.markdown('<p class="section-header">🔍 Ask Your Question</p>', unsafe_allow_html=True)
    
    # Query input
    query_text = st.text_area(
        "Type your question in natural language",
        placeholder="e.g., What are the top 10 customer states by revenue?",
        height=100,
        key="query_input",
        value=st.session_state.get('example_query', '')
    )
    
    # Clear example query after use
    if 'example_query' in st.session_state:
        del st.session_state.example_query
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
    with col_btn1:
        analyze_button = st.button("🚀 Run Query", type="primary", use_container_width=True)
    with col_btn2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_button:
        st.rerun()
    
    # Process query
    if analyze_button and query_text.strip():
        start_time = time.time()
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Parse Intent
            status_text.text("🧠 Step 1/3: Parsing natural language query...")
            progress_bar.progress(33)
            
            intent_result = parser.parse(query_text)
            
            if not intent_result.success:
                st.error(f"❌ Could not understand the question: {intent_result.error}")
                progress_bar.empty()
                status_text.empty()
                return
            
            intent = intent_result.intent
            
            # Step 2: Generate SQL
            status_text.text("⚙️ Step 2/3: Generating SQL query...")
            progress_bar.progress(66)
            
            sql_result = generator.generate(intent)
            
            if not sql_result['is_valid']:
                st.error(f"❌ Could not generate valid SQL: {', '.join(sql_result['errors'])}")
                progress_bar.empty()
                status_text.empty()
                return
            
            # Step 3: Execute SQL
            status_text.text("🔄 Step 3/3: Executing query...")
            progress_bar.progress(100)
            
            exec_result = executor.execute(sql_result['sql'])
            
            if not exec_result.success:
                st.error(f"❌ Query execution failed: {exec_result.error}")
                progress_bar.empty()
                status_text.empty()
                return
            
            # Complete
            status_text.text("✅ Query completed successfully!")
            time.sleep(0.3)
            progress_bar.empty()
            status_text.empty()
            
            total_time = (time.time() - start_time) * 1000
            
            # Store in history
            st.session_state.query_history.append({
                'query': query_text,
                'execution_time': total_time,
                'timestamp': datetime.now(),
                'rows': exec_result.row_count
            })
            
            # Success message
            st.success(f"✅ Query executed successfully: {exec_result.row_count:,} row{'' if exec_result.row_count == 1 else 's'} returned in {total_time:.0f}ms")
            
            # ============================================================================
            # RESULTS SECTION WITH SMART VISUALIZATION
            # ============================================================================
            
            st.markdown('<p class="section-header">📊 Query Results</p>', unsafe_allow_html=True)
            
            # Select chart type
            chart_config = chart_selector.select_chart(intent, exec_result.data)
            
            # Render visualization
            if chart_config['type'] == 'metric':
                # Single metric display
                st.markdown(f"""
                    <div class="metric-box" style="text-align: center; max-width: 400px; margin: 0 auto 2rem auto;">
                        <div class="metric-label">{chart_config['label']}</div>
                        <div class="metric-value">{chart_config['value']:,.2f}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                # Render Plotly chart
                fig = chart_renderer.render(chart_config)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            # Data table (always show)
            st.markdown("### 📋 Data Table")
            st.dataframe(
                exec_result.data,
                use_container_width=True,
                height=min(400, (len(exec_result.data) + 1) * 35 + 3)
            )
            
            # ============================================================================
            # END VISUALIZATION SECTION
            # ============================================================================
            
            # Detailed Information (Collapsible)
            with st.expander("🔍 Query Details", expanded=False):
                tab1, tab2, tab3 = st.tabs(["📝 Intent Analysis", "💻 Generated SQL", "⚡ Execution Stats"])
                
                with tab1:
                    st.markdown("**Intent Type:**")
                    st.code(intent.intent_type.upper())
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("**Metrics:**")
                        for metric in intent.metrics:
                            st.markdown(f"- `{metric}`")
                    
                    with col_b:
                        st.markdown("**Dimensions:**")
                        if intent.dimensions:
                            for dim in intent.dimensions:
                                st.markdown(f"- `{dim}`")
                        else:
                            st.caption("None")
                    
                    if intent.filters:
                        st.markdown("**Filters:**")
                        for f in intent.filters:
                            st.markdown(f"- `{f.dimension}` {f.operator} `{f.value}`")
                    
                    st.markdown(f"**Confidence:** {intent.confidence:.1%}")
                
                with tab2:
                    st.markdown("**Generated SQL Query:**")
                    st.code(exec_result.sql, language="sql")
                    
                    if sql_result.get('warnings'):
                        st.warning("⚠️ Warnings:\n" + "\n".join(sql_result['warnings']))
                
                with tab3:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Execution Time", f"{exec_result.execution_time_ms:.2f}ms")
                    with col2:
                        st.metric("Rows Returned", f"{exec_result.row_count:,}")
                    with col3:
                        st.metric("Columns", f"{len(exec_result.data.columns)}")
                    with col4:
                        st.metric("Result Hash", exec_result.result_hash[:8] + "...")
            
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ An unexpected error occurred: {str(e)}")
            with st.expander("🐛 Error Details"):
                st.exception(e)
    
    elif analyze_button:
        st.warning("⚠️ Please enter a question to analyze.")
    
    # Footer info
    st.markdown("---")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.caption("🎯 **Powered by:** OpenRouter GPT-4o + DuckDB")
    with col_f2:
        st.caption("🔒 **Security:** Multi-layer SQL validation")
    with col_f3:
        st.caption("⚡ **Performance:** Optimized query execution")


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
