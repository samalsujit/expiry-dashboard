# components/styles.py
import streamlit as st

def inject_dashboard_theme():
    """Inject clean enterprise dashboard styling while keeping the header and sidebar toggle safe"""
    st.markdown("""
    <style>
        /* Base App Background */
        .stApp {
            background-color: #f8fafc !important;
        }
        
        /* Keep header clean and transparent without hiding the toolbar/toggle */
        header[data-testid="stHeader"] {
            background: transparent !important;
            border: none !important;
        }
        
        /* Hide only the deploy button, leaving the sidebar toggle container visible */
        .stAppDeployButton {
            display: none !important;
        }
        
        /* Sidebar Container Polish */
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid #e2e8f0 !important;
        }
        
        /* Sidebar Navigation Buttons */
        [data-testid="stSidebar"] div[data-testid="stButton"] button {
            width: 100%;
            border: none !important;
            background-color: transparent !important;
            color: #64748b !important;
            text-align: left !important;
            padding: 10px 15px !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            display: flex !important;
            justify-content: flex-start !important;
            box-shadow: none !important;
            transition: all 0.2s ease !important;
            font-size: 14px !important;
        }
        
        [data-testid="stSidebar"] div[data-testid="stButton"] button:hover {
            background-color: #f1f5f9 !important;
            color: #0f172a !important;
        }
        
        [data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] {
            background-color: #f0fdf4 !important;
            color: #16a34a !important;
        }

        /* General Form & Widget Polish */
        .stTextInput > div > div > input, .stSelectbox > div > div {
            border-radius: 8px;
            border: 1px solid #cbd5e1;
            box-shadow: none;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #16a34a;
            box-shadow: 0 0 0 2px rgba(22, 163, 74, 0.1);
        }
        
        .stButton > button {
            border-radius: 8px !important;
            font-weight: 600 !important;
        }
        
        .stMetric {
            background: white;
            border-radius: 12px;
            padding: 0.75rem 1rem;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
    </style>
    """, unsafe_allow_html=True)