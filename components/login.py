# components/login.py
import streamlit as st
import base64
import os
import re
import time

def get_base64_image(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def show_login():
    bg = get_base64_image("assets/images/warehouse.jpeg")
    if not bg:
        bg = get_base64_image("assets/images/warehouse.jpg")

    bg_css = f'url("data:image/jpeg;base64,{bg}")' if bg else 'none'

    st.markdown(f"""
    <style>
    #MainMenu {{visibility:hidden;}}
    footer {{visibility:hidden;}}

    .stApp {{
        background: linear-gradient(rgba(8,40,22,.75), rgba(8,40,22,.85)), {bg_css};
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    .stTextInput label {{
        color: #0f2d1d !important;
        font-weight: 600 !important;
    }}
    
    .stTextInput input {{
        color: #111111 !important;
        -webkit-text-fill-color: #111111 !important;
        background-color: #f8f9fa !important;
    }}
    
    /* Professional brand logo badge styling */
    .login-logo-container {{
        display: flex;
        justify-content: center;
        margin-bottom: 12px;
    }}
    .login-logo-badge {{
        background: #197A31;
        color: #FEDB00;
        font-weight: 800;
        font-size: 22px;
        padding: 10px 20px;
        border-radius: 14px;
        box-shadow: 0 4px 14px rgba(25, 122, 49, 0.25);
        letter-spacing: -0.5px;
    }}
    .login-logo-badge span {{
        color: #ffffff;
    }}
    </style>
    """, unsafe_allow_html=True)

    # Center the login box horizontally using columns
    _, col, _ = st.columns([1, 1.1, 1])

    with col:
        with st.container(border=True):
            # Professional brand logo badge
            st.markdown("""
            <div class="login-logo-container">
                <div class="login-logo-badge">Expiry<span>Dash</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<h3 style='text-align: center; color: #0f2d1d; margin-top: 5px; margin-bottom: 5px;'>Expiry Removal Dashboard</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #666666; font-size: 14px; margin-bottom: 25px;'>Sign in to access your dashboard</p>", unsafe_allow_html=True)

            email = st.text_input(
                "Email Address",
                placeholder="name@noon.com",
                key="login_email"
            )

            password = ""
            # Dynamically show password input ONLY if admin email is entered
            if email and email.lower().strip() == "susamal@noon.com":
                password = st.text_input(
                    "Admin Password",
                    type="password",
                    placeholder="Enter admin password",
                    key="login_password"
                )

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

            submitted = st.button(
                "Continue",
                use_container_width=True,
                type="primary"
            )

    if submitted:
        ADMIN_EMAIL = "susamal@noon.com"
        ADMIN_PASSWORD = "AdminSecurePassword123!"

        if not email:
            st.error("Please enter your email address.")
        elif not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', email):
            st.error("Please enter a valid email address.")
        elif not email.lower().endswith("@noon.com"):
            st.error("Access restricted to @noon.com email addresses.")
        else:
            if email.lower() == ADMIN_EMAIL:
                if password != ADMIN_PASSWORD:
                    st.error("❌ Incorrect Admin password.")
                    return
                st.session_state.username = "Sujit Kumar"
                st.session_state.user_role = "Admin"
            else:
                st.session_state.username = email.split("@")[0].title()
                st.session_state.user_role = "Viewer"

            st.session_state.logged_in = True
            st.session_state.user_email = email

            st.success("✅ Login successful! Redirecting...")
            time.sleep(0.5)
            st.rerun()
