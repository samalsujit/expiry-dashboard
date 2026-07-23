# components/header.py
import streamlit as st
from datetime import datetime

def show_header():
    """Show the clean dashboard header"""
    
    now = datetime.now()
    page_name = st.session_state.get("current_page", "overview")
    page_display = page_name.replace("_", " ").title()
    
    formatted_date = now.strftime("%A, %d %B %Y")
    formatted_time = now.strftime("%I:%M %p")
    refresh_time = now.strftime("%d %b %Y %H:%M")
    
    st.markdown(f"""
    <div style="padding-bottom: 20px; margin-bottom: 30px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: flex-start;">
        <div>
            <h1 style="font-size: 28px; font-weight: 800; color: #0f172a; margin: 0 0 5px 0; padding: 0;">
                {page_display}
            </h1>
            <p style="font-size: 13px; color: #64748b; margin: 0;">
                🇸🇦 Saudi Arabia | Last Refresh: {refresh_time}
            </p>
        </div>
        <div style="text-align: right; font-size: 13px; color: #64748b; line-height: 1.4;">
            <strong style="color: #0f172a;">{formatted_date}</strong><br>
            {formatted_time}
        </div>
    </div>
    """, unsafe_allow_html=True)