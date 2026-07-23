# components/sidebar.py
import streamlit as st

def show_sidebar():
    """Render the full enterprise sidebar with user profile and navigation"""
    
    with st.sidebar:
        # ── Brand Header ──
        st.markdown("""
        <div style="padding: 10px 5px 25px 5px; display: flex; align-items: center; gap: 12px;">
            <div style="background: #f0fdf4; color: #16a34a; width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 18px;">
                N
            </div>
            <div style="font-size: 20px; font-weight: 800; color: #0f172a; letter-spacing: -0.5px;">
                Dashboard
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ── Safe User Profile Extraction ──
        username = st.session_state.get("username", "Guest")
        if not username or not isinstance(username, str):
            username = "Guest"
            
        user_role = st.session_state.get("user_role", "Viewer")
        if not user_role:
            user_role = "Viewer"
            
        initial = username[0].upper() if username else "U"
        
        st.markdown(f"""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; margin-bottom: 25px; display: flex; align-items: center; gap: 12px;">
            <div style="background: #1e293b; color: white; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 14px;">
                {initial}
            </div>
            <div style="display: flex; flex-direction: column;">
                <span style="font-size: 13px; font-weight: 700; color: #0f172a;">{username}</span>
                <span style="font-size: 11px; font-weight: 600; color: #16a34a; background: #dcfce7; padding: 2px 6px; border-radius: 4px; width: fit-content; margin-top: 3px;">
                    {user_role}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ── Navigation Menu ──
        st.markdown("<div style='margin-bottom: 5px; font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase;'>Menu</div>", unsafe_allow_html=True)
        
        nav_items = [
            {"label": "Overview", "icon": "📊", "page": "overview"},
            {"label": "Analytics", "icon": "📈", "page": "analytics"},
            {"label": "Forecast", "icon": "🔮", "page": "forecast"},
            {"label": "Exceptions", "icon": "⚠️", "page": "exceptions"},
            {"label": "Reports", "icon": "📄", "page": "reports"},
        ]
        
        if user_role in ["Admin", "Manager"]:
            nav_items.append({"label": "Upload", "icon": "📤", "page": "upload"})
            nav_items.append({"label": "Administration", "icon": "⚙️", "page": "administration"})
        
        current_page = st.session_state.get("current_page", "overview")
        
        # Render Buttons safely
        for item in nav_items:
            is_active = (current_page == item["page"])
            button_type = "primary" if is_active else "secondary"
            
            if st.button(
                f"{item['icon']} \u00A0\u00A0 {item['label']}",
                key=f"nav_{item['page']}",
                use_container_width=True,
                type=button_type
            ):
                st.session_state.current_page = item["page"]
                st.rerun()
        
        # ── Logout ──
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 \u00A0\u00A0 Logout", use_container_width=True, key="logout_btn", type="secondary"):
            st.session_state.logged_in = False
            st.session_state.username = "Guest"
            st.session_state.user_role = "Viewer"
            st.session_state.user_email = ""
            st.rerun()
            
        return st.session_state.get("current_page", "overview")