"""
UI Styling and Theme Configuration
Sprint 2, Ticket 8: Theme System
"""

# Color Palette
COLORS = {
    # Primary colors
    'primary': '#667eea',
    'primary_dark': '#764ba2',
    'primary_light': '#a5b4fc',
    
    # Accent colors
    'accent': '#f59e0b',
    'accent_light': '#fbbf24',
    
    # Semantic colors
    'success': '#22c55e',
    'success_light': '#dcfce7',
    'warning': '#f59e0b',
    'warning_light': '#fef3c7',
    'error': '#ef4444',
    'error_light': '#fee2e2',
    'info': '#3b82f6',
    'info_light': '#eff6ff',
    
    # Neutral colors
    'gray_50': '#f8fafc',
    'gray_100': '#f1f5f9',
    'gray_200': '#e2e8f0',
    'gray_300': '#cbd5e1',
    'gray_400': '#94a3b8',
    'gray_500': '#64748b',
    'gray_600': '#475569',
    'gray_700': '#334155',
    'gray_800': '#1e293b',
    'gray_900': '#0f172a',
    
    # Background colors
    'bg_primary': 'white',
    'bg_secondary': '#f8fafc',
    'bg_tertiary': '#f1f5f9',
    
    # Text colors
    'text_primary': '#1e293b',
    'text_secondary': '#64748b',
    'text_tertiary': '#94a3b8',
}


# Typography
FONTS = {
    'primary': "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    'mono': "'JetBrains Mono', 'Courier New', monospace",
}

FONT_SIZES = {
    'xs': '0.75rem',
    'sm': '0.85rem',
    'base': '1rem',
    'lg': '1.1rem',
    'xl': '1.25rem',
    '2xl': '1.5rem',
    '3xl': '2rem',
    '4xl': '2.5rem',
}

FONT_WEIGHTS = {
    'light': 300,
    'normal': 400,
    'medium': 500,
    'semibold': 600,
    'bold': 700,
}


# Spacing
SPACING = {
    'xs': '0.25rem',
    'sm': '0.5rem',
    'md': '1rem',
    'lg': '1.5rem',
    'xl': '2rem',
    '2xl': '2.5rem',
    '3xl': '3rem',
}


# Border Radius
RADIUS = {
    'sm': '4px',
    'md': '8px',
    'lg': '12px',
    'xl': '16px',
    'full': '9999px',
}


# Shadows
SHADOWS = {
    'sm': '0 2px 4px rgba(0, 0, 0, 0.06)',
    'md': '0 4px 12px rgba(0, 0, 0, 0.08)',
    'lg': '0 6px 20px rgba(0, 0, 0, 0.12)',
    'xl': '0 10px 40px rgba(102, 126, 234, 0.4)',
}


# Chart Color Schemes
CHART_COLORS = {
    'viridis': ['#440154', '#31688e', '#35b779', '#fde724'],
    'sunset': ['#667eea', '#764ba2', '#f093fb', '#f5576c'],
    'ocean': ['#2e3192', '#1bffff', '#00c9ff', '#92fe9d'],
    'warm': ['#ff9966', '#ff5e62', '#eb144c', '#fcb900'],
    'cool': ['#4facfe', '#00f2fe', '#43e97b', '#38f9d7'],
}


# Gradients
GRADIENTS = {
    'primary': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'success': 'linear-gradient(135deg, #22c55e 0%, #10b981 100%)',
    'warning': 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
    'error': 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
    'background': 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
    'sidebar': 'linear-gradient(180deg, #1e293b 0%, #334155 100%)',
}


# Chart Configuration
CHART_CONFIG = {
    'font_family': FONTS['primary'],
    'font_size': 12,
    'height': 500,
    'margin': {'l': 60, 'r': 40, 't': 60, 'b': 60},
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'paper_bgcolor': 'rgba(0,0,0,0)',
}


# Component Styles
COMPONENT_STYLES = {
    'card': {
        'background': COLORS['bg_primary'],
        'padding': SPACING['lg'],
        'border_radius': RADIUS['lg'],
        'box_shadow': SHADOWS['md'],
    },
    
    'metric_card': {
        'background': COLORS['bg_primary'],
        'padding': SPACING['lg'],
        'border_radius': RADIUS['lg'],
        'box_shadow': SHADOWS['sm'],
        'border_left': f"4px solid {COLORS['primary']}",
    },
    
    'header': {
        'background': GRADIENTS['primary'],
        'padding': f"{SPACING['xl']} {SPACING['2xl']}",
        'border_radius': RADIUS['xl'],
        'color': 'white',
        'box_shadow': SHADOWS['xl'],
    },
    
    'button': {
        'background': GRADIENTS['primary'],
        'color': 'white',
        'border_radius': RADIUS['md'],
        'padding': f"{SPACING['md']} {SPACING['xl']}",
        'font_weight': FONT_WEIGHTS['semibold'],
        'box_shadow': f"0 4px 12px rgba(102, 126, 234, 0.3)",
    },
}


# Animation Durations
ANIMATIONS = {
    'fast': '0.1s',
    'normal': '0.2s',
    'slow': '0.3s',
}


# Breakpoints (for responsive design)
BREAKPOINTS = {
    'sm': '640px',
    'md': '768px',
    'lg': '1024px',
    'xl': '1280px',
}


def get_custom_css() -> str:
    """
    Generate complete custom CSS for the application.
    
    Returns:
        CSS string for Streamlit markdown injection
    """
    return f"""
        <style>
        /* Import Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
        
        /* Global Styles */
        * {{
            font-family: {FONTS['primary']};
        }}
        
        .main {{
            background: {GRADIENTS['background']};
            padding: {SPACING['xl']};
        }}
        
        /* Headers */
        .main-header {{
            background: {GRADIENTS['primary']};
            padding: {SPACING['xl']} {SPACING['2xl']};
            border-radius: {RADIUS['xl']};
            color: white;
            margin-bottom: {SPACING['xl']};
            box-shadow: {SHADOWS['xl']};
        }}
        
        .main-header h1 {{
            font-size: {FONT_SIZES['4xl']};
            font-weight: {FONT_WEIGHTS['bold']};
            margin: 0;
            letter-spacing: -0.5px;
        }}
        
        .main-header p {{
            font-size: {FONT_SIZES['lg']};
            margin: {SPACING['sm']} 0 0 0;
            opacity: 0.95;
            font-weight: {FONT_WEIGHTS['light']};
        }}
        
        /* Section Headers */
        .section-header {{
            font-size: {FONT_SIZES['2xl']};
            font-weight: {FONT_WEIGHTS['bold']};
            color: {COLORS['text_primary']};
            margin: {SPACING['xl']} 0 {SPACING['md']} 0;
            padding-bottom: {SPACING['sm']};
            border-bottom: 3px solid {COLORS['primary']};
            display: inline-block;
        }}
        
        /* Cards */
        .metric-card {{
            background: {COLORS['bg_primary']};
            padding: {SPACING['lg']};
            border-radius: {RADIUS['lg']};
            box-shadow: {SHADOWS['sm']};
            border-left: 4px solid {COLORS['primary']};
            transition: transform {ANIMATIONS['normal']} ease, box-shadow {ANIMATIONS['normal']} ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: {SHADOWS['lg']};
        }}
        
        .metric-label {{
            font-size: {FONT_SIZES['sm']};
            font-weight: {FONT_WEIGHTS['semibold']};
            color: {COLORS['text_secondary']};
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: {SPACING['sm']};
        }}
        
        .metric-value {{
            font-size: {FONT_SIZES['3xl']};
            font-weight: {FONT_WEIGHTS['bold']};
            color: {COLORS['text_primary']};
            line-height: 1;
        }}
        
        /* Buttons */
        .stButton > button {{
            background: {GRADIENTS['primary']};
            color: white;
            border: none;
            border-radius: {RADIUS['md']};
            padding: {SPACING['md']} {SPACING['xl']};
            font-weight: {FONT_WEIGHTS['semibold']};
            font-size: {FONT_SIZES['base']};
            transition: all {ANIMATIONS['slow']} ease;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background: {GRADIENTS['sidebar']};
        }}
        
        [data-testid="stSidebar"] * {{
            color: white !important;
        }}
        
        /* Code Blocks */
        code {{
            background: {COLORS['gray_100']};
            padding: {SPACING['xs']} {SPACING['sm']};
            border-radius: {RADIUS['sm']};
            font-family: {FONTS['mono']};
            font-size: {FONT_SIZES['sm']};
        }}
        
        .stCodeBlock {{
            border-radius: {RADIUS['md']};
            border: 1px solid {COLORS['gray_200']};
        }}
        
        /* Messages */
        .stSuccess {{
            background: {COLORS['success_light']};
            border-left: 4px solid {COLORS['success']};
            border-radius: {RADIUS['md']};
        }}
        
        .stError {{
            background: {COLORS['error_light']};
            border-left: 4px solid {COLORS['error']};
            border-radius: {RADIUS['md']};
        }}
        
        .stWarning {{
            background: {COLORS['warning_light']};
            border-left: 4px solid {COLORS['warning']};
            border-radius: {RADIUS['md']};
        }}
        
        /* Expanders */
        .streamlit-expanderHeader {{
            background: {COLORS['gray_50']};
            border-radius: {RADIUS['md']};
            font-weight: {FONT_WEIGHTS['semibold']};
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: {SPACING['sm']};
        }}
        
        .stTabs [data-baseweb="tab"] {{
            border-radius: {RADIUS['md']} {RADIUS['md']} 0 0;
            padding: {SPACING['md']} {SPACING['lg']};
            font-weight: {FONT_WEIGHTS['semibold']};
        }}
        
        /* Hide Streamlit Branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        </style>
    """


# Icon mappings
ICONS = {
    'query': '🔍',
    'analytics': '📊',
    'database': '💾',
    'api': '🔌',
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'chart': '📈',
    'table': '📋',
    'settings': '⚙️',
    'history': '📜',
    'example': '💡',
    'loading': '⏳',
    'time': '⏱️',
    'rocket': '🚀',
    'brain': '🧠',
    'gear': '⚙️',
    'refresh': '🔄',
    'trash': '🗑️',
}
