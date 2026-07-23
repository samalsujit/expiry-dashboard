# app.py
import streamlit as st

# Must be first
st.set_page_config(
    page_title="Expiry Removal Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import components
from components.login import show_login
from components.styles import inject_dashboard_theme
from components.sidebar import show_sidebar
from components.header import show_header
from components.footer import show_footer

# Import views
from views.overview import show_overview
from views.analytics import show_analytics
from views.forecast import show_forecast
from views.exceptions import show_exceptions
from views.reports import show_reports
from views.upload import show_upload
from views.administration import show_administration

# Import utilities
from utils.session import initialize_session

# Initialize session
initialize_session()

# ----- LOGIN STATE CHECK -----
if not st.session_state.get("logged_in", False):
    show_login()
    st.stop()

# ----- FULL DASHBOARD SETUP -----
inject_dashboard_theme()

selected = show_sidebar()
show_header()

if selected == "overview":
    show_overview()
elif selected == "analytics":
    show_analytics()
elif selected == "forecast":
    show_forecast()
elif selected == "exceptions":
    show_exceptions()
elif selected == "reports":
    show_reports()
elif selected == "upload":
    show_upload()
elif selected == "administration":
    show_administration()
else:
    show_overview()

show_footer()