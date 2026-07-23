import streamlit as st
import os


def load_css(css_path):
    """Load CSS file and inject into Streamlit"""
    try:
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Try multiple paths
        possible_paths = [
            css_path,
            os.path.join(project_root, css_path),
            os.path.join(project_root, "assets", "css", os.path.basename(css_path)),
            os.path.join(os.getcwd(), css_path),
            os.path.join(os.getcwd(), "assets", "css", os.path.basename(css_path)),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, "r") as f:
                    css = f.read()
                st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
                return True
        
        # If file not found, use inline fallback styles
        st.markdown("""
        <style>
            .login-card {
                background: white;
                border-radius: 24px;
                padding: 40px;
                max-width: 480px;
                margin: auto;
                box-shadow: 0 30px 80px rgba(0,0,0,0.3);
            }
            .login-title {
                text-align: center;
                font-size: 24px;
                font-weight: 700;
            }
            .login-subtitle {
                text-align: center;
                color: #666;
            }
        </style>
        """, unsafe_allow_html=True)
        return False
    except Exception as e:
        st.warning(f"Error loading CSS: {e}")
        return False


def format_currency(value, currency="SAR"):
    if value is None or (isinstance(value, float) and value != value):
        return "N/A"
    return f"{currency} {value:,.2f}"


def format_quantity(value):
    if value is None or (isinstance(value, float) and value != value):
        return "N/A"
    return f"{value:,.0f}"


def format_percent(value, decimals=1):
    if value is None or (isinstance(value, float) and value != value):
        return "N/A"
    return f"{value:.{decimals}f}%"


def format_days(value):
    if value is None or (isinstance(value, float) and value != value):
        return "N/A"
    if value == 0:
        return "Today"
    elif value < 0:
        return f"{abs(value):.0f} days ago"
    else:
        return f"{value:.0f} days"


def format_number(value):
    if value is None or (isinstance(value, float) and value != value):
        return "N/A"
    return f"{value:,.0f}"