# utils/session.py
import streamlit as st
import os
import pandas as pd
from services.processor import process_dataframe, clean_dataframe


def initialize_session():
    """Initialize all session state variables and load shared server data if available"""
    
    # Authentication
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = "Guest"
    if "user_role" not in st.session_state:
        st.session_state.user_role = "Viewer"
    if "user_email" not in st.session_state:
        st.session_state.user_email = ""
    
    # Navigation
    if "current_page" not in st.session_state:
        st.session_state.current_page = "overview"
    
    # Load shared inventory file from disk if it exists
    shared_path = "data/shared_inventory.csv"
    shared_df = None
    
    if os.path.exists(shared_path):
        try:
            shared_df = pd.read_csv(shared_path)
            shared_df = clean_dataframe(shared_df)
        except Exception:
            shared_df = None

    # Data state initialization using shared data
    if "original_dataframe" not in st.session_state:
        st.session_state.original_dataframe = shared_df
        
    if "uploaded_dataframe" not in st.session_state:
        st.session_state.uploaded_dataframe = shared_df
        
    if "dashboard_data" not in st.session_state:
        if shared_df is not None and not shared_df.empty:
            try:
                st.session_state.dashboard_data = process_dataframe(shared_df, expiry_window="All Inventory")
            except Exception:
                st.session_state.dashboard_data = None
        else:
            st.session_state.dashboard_data = None
            
    if "filtered_dataframe" not in st.session_state:
        st.session_state.filtered_dataframe = shared_df
    
    # Filters
    if "filters" not in st.session_state:
        st.session_state.filters = {
            "expiry_window": "All Inventory",
            "category": "All Categories",
            "zsku": "All ZSKU",
            "store": "All Stores",
            "search": ""
        }
    
    # Upload history
    if "upload_history" not in st.session_state:
        st.session_state.upload_history = []
    
    # Users
    if "users" not in st.session_state:
        st.session_state.users = [
            {"Username": "Sujit Kumar", "Role": "Admin", "Email": "susamal@noon.com", "Status": "Active"},
            {"Username": "Manager", "Role": "Manager", "Email": "manager@noon.com", "Status": "Active"},
        ]
    
    # Report defaults
    if "report_defaults" not in st.session_state:
        st.session_state.report_defaults = {
            "default_report_type": "Executive Summary",
            "default_format": "CSV",
            "include_charts": True,
            "include_tables": True,
            "include_summary": True
        }


def reset_session():
    """Reset all session state"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    initialize_session()
