# components/login.py
import streamlit as st
import re
import time
import base64
import os

def get_base64_image(image_path):
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
    except Exception:
        pass
    return ""

def show_login():
    """Renders a clean, centered login card with a blurred warehouse background."""
    
    warehouse_b64 = get_base64_image("assets/images/warehouse.jpeg")
    if not warehouse_b64:
        warehouse_b64 = get_base64_image("assets/images/warehouse.jpg")
    
    bg_image_css = f'url("data:image/jpeg;base64,{warehouse_b64}")' if warehouse_b64 else 'none'

    st.markdown(f"""
    <style>
        #MainMenu {{
            visibility: hidden;
        }}
        footer {{
            visibility: hidden;
        }}
        
        .stApp {{
            background: linear-gradient(rgba(13, 43, 26, 0.75), rgba(13, 43, 26, 0.85)), {bg_image_css} !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }}
        
        [data-testid="stMainBlockContainer"] {{
            background: #ffffff !important;
            border-radius: 24px !important;
            padding: 45px 40px 35px !important;
            max-width: 440px !important;
            margin: 15vh auto 0 auto !important;
            box-shadow: 0 30px 80px rgba(0, 0, 0, 0.4) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }}
        
        .login-icon {{
            text-align: center;
            font-size: 48px;
            margin-bottom: 0.5rem;
        }}
        
        .login-title {{
            text-align: center;
            font-size: 26px;
            font-weight: 700;
            color: #0d2b1a;
            margin-bottom: 0.25rem;
        }}
        
        .login-subtitle {{
            text-align: center;
            color: #6c757d;
            font-size: 15px;
            margin-bottom: 28px;
        }}
        
        [data-testid="stForm"] {{
            border: none !important;
            padding: 0 !important;
            background: transparent !important;
        }}
        
        .stTextInput > label {{
            color: #0d2b1a !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
        }}
        
        .stTextInput input {{
            height: 50px !important;
            border-radius: 12px !important;
            border: 1.5px solid #e8ebef !important;
            font-size: 15px !important;
            padding: 0 18px !important;
            background: #fafbfc !important;
            color: #0d2b1a !important;
        }}
        
        .stTextInput input:focus {{
            border-color: #197A31 !important;
            box-shadow: 0 0 0 4px rgba(25, 122, 49, 0.1) !important;
        }}
        
        .stButton button[kind="primary"], div[data-testid="stForm"] button {{
            height: 50px !important;
            border-radius: 12px !important;
            background: #197A31 !important;
            color: white !important;
            font-size: 17px !important;
            font-weight: 700 !important;
            border: none !important;
            width: 100% !important;
        }}
        
        .stButton button[kind="primary"]:hover, div[data-testid="stForm"] button:hover {{
            background: #146628 !important;
        }}
        
        .divider {{
            display: flex;
            align-items: center;
            margin: 1.5rem 0;
            gap: 1rem;
        }}
        
        .divider .line {{
            flex: 1;
            height: 1px;
            background: #e8ebef;
        }}
        
        .divider .text {{
            color: #adb5bd;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 22px;
            color: #8a8f98;
            font-size: 12px;
        }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-icon">📊</div>
    <div class="login-title">Expiry Removal Dashboard</div>
    <div class="login-subtitle">Sign in to access your dashboard</div>
    """, unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        email = st.text_input(
            "Email Address",
            placeholder="Enter your email address",
            key="login_email"
        )
        submitted = st.form_submit_button("Continue", use_container_width=True)

    if submitted:
        if not email:
            st.error("Please enter your email address.")
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            st.error("Please enter a valid email address.")
        elif not email.lower().endswith("@noon.com"):
            st.error("Access restricted to @noon.com email addresses.")
        else:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            
            if email.lower() == "susamal@noon.com":
                st.session_state.username = "Sujit Kumar"
                st.session_state.user_role = "Admin"
            else:
                st.session_state.username = email.split("@")[0].title()
                st.session_state.user_role = "Viewer"
            
            st.success("✅ Login successful! Redirecting…")
            time.sleep(0.5)
            st.rerun()

    st.markdown("""
    <div class="divider">
        <div class="line"></div>
        <span class="text">OR</span>
        <div class="line"></div>
    </div>
    """, unsafe_allow_html=True)

    st.button(
        "Sign in with Google", 
        disabled=True, 
        use_container_width=True, 
        key="google_login"
    )

    st.markdown("""
    <div class="footer">
        🔒 Enterprise Security • Inventory Management Platform
    </div>
    """, unsafe_allow_html=True)