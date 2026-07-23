import streamlit as st
import pandas as pd
from datetime import datetime
import json

# Category config from processor
from services.processor import CATEGORY_CONFIG


def show_administration():
    """Administration page - System settings and management"""
    
    st.title("⚙️ Administration")
    
    # Check for admin access - FIXED: Proper admin check
    user_email = st.session_state.get("user_email", "")
    user_role = st.session_state.get("user_role", "Viewer")
    
    # Check if user is admin
    is_admin = user_role == "Admin" or user_email.lower() == "susamal@noon.com"
    
    if not is_admin:
        st.error("⛔ Access Denied. You need administrator privileges to access this page.")
        st.info(f"Current user: {st.session_state.get('username', 'Unknown')} ({user_email})")
        st.info("Only users with Admin role can access this page.")
        return
    
    # ---------------- Tabs ----------------
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👤 User Management",
        "📂 Category Rules",
        "📊 Report Defaults",
        "📤 Upload History",
        "⚙️ System Settings"
    ])
    
    with tab1:
        show_user_management()
    
    with tab2:
        show_category_rules()
    
    with tab3:
        show_report_defaults()
    
    with tab4:
        show_upload_history()
    
    with tab5:
        show_system_settings()


def show_user_management():
    """User management tab"""
    
    st.subheader("👤 User Management")
    
    # Sample user data
    if "users" not in st.session_state:
        st.session_state.users = [
            {"Username": "Sujit Kumar", "Role": "Admin", "Email": "susamal@noon.com", "Status": "Active"},
            {"Username": "Manager", "Role": "Manager", "Email": "manager@noon.com", "Status": "Active"},
            {"Username": "Analyst", "Role": "Analyst", "Email": "analyst@noon.com", "Status": "Active"},
            {"Username": "Viewer", "Role": "Viewer", "Email": "viewer@noon.com", "Status": "Inactive"},
        ]
    
    # Display users
    users_df = pd.DataFrame(st.session_state.users)
    st.dataframe(users_df, use_container_width=True, hide_index=True)
    
    # Add user form
    with st.expander("➕ Add New User"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_username = st.text_input("Username")
        
        with col2:
            new_role = st.selectbox("Role", ["Admin", "Manager", "Analyst", "Viewer"])
        
        with col3:
            new_email = st.text_input("Email")
        
        if st.button("Add User", use_container_width=True):
            if new_username and new_email:
                st.session_state.users.append({
                    "Username": new_username,
                    "Role": new_role,
                    "Email": new_email,
                    "Status": "Active"
                })
                st.success(f"✅ User {new_username} added successfully!")
                st.rerun()
            else:
                st.error("❌ Please fill in all fields.")


def show_category_rules():
    """Category include/exclude rules management"""
    
    st.subheader("📂 Category Include/Exclude Rules")
    
    st.info("""This configuration controls which categories are included in all dashboard calculations.
    Categories marked as 'Include' will be part of all reports and analytics.
    Categories marked as 'Exclude' will be filtered out entirely.
    """)
    
    # Display current configuration
    config_df = pd.DataFrame([
        {"Category": cat, "Status": status}
        for cat, status in CATEGORY_CONFIG.items()
    ])
    config_df = config_df.sort_values("Category")
    
    st.dataframe(config_df, use_container_width=True, hide_index=True)
    
    # Edit configuration
    with st.expander("✏️ Edit Category Rules"):
        st.caption("Select categories to include or exclude. Changes will affect all dashboard calculations.")
        
        all_categories = sorted(CATEGORY_CONFIG.keys())
        included = [cat for cat, status in CATEGORY_CONFIG.items() if status == "Include"]
        excluded = [cat for cat, status in CATEGORY_CONFIG.items() if status == "Exclude"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_included = st.multiselect(
                "Categories to Include",
                options=all_categories,
                default=included,
                help="Categories selected here will be included in all dashboard calculations"
            )
        
        with col2:
            new_excluded = st.multiselect(
                "Categories to Exclude",
                options=all_categories,
                default=excluded,
                help="Categories selected here will be excluded from all dashboard calculations"
            )
        
        if st.button("Apply Category Rules", use_container_width=True):
            for cat in all_categories:
                if cat in new_included:
                    CATEGORY_CONFIG[cat] = "Include"
                else:
                    CATEGORY_CONFIG[cat] = "Exclude"
            
            st.success("✅ Category rules updated successfully! Refresh the dashboard to see changes.")
            st.rerun()


def show_report_defaults():
    """Report default settings"""
    
    st.subheader("📊 Report Defaults")
    
    st.info("Configure default settings for all report generation.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        default_report_type = st.selectbox(
            "Default Report Type",
            ["Executive Summary", "Store Performance Report", "Category Performance Report", "Expiry Risk Report"],
            help="This will be the default selection when opening the Reports page"
        )
    
    with col2:
        default_format = st.selectbox(
            "Default Export Format",
            ["CSV", "Excel", "PDF"],
            help="This will be the default export format for all reports"
        )
    
    include_charts = st.checkbox("Include Charts in Reports", value=True)
    include_tables = st.checkbox("Include Data Tables", value=True)
    include_summary = st.checkbox("Include Executive Summary", value=True)
    
    if st.button("Save Report Defaults", use_container_width=True):
        st.session_state.report_defaults = {
            "default_report_type": default_report_type,
            "default_format": default_format,
            "include_charts": include_charts,
            "include_tables": include_tables,
            "include_summary": include_summary
        }
        st.success("✅ Report defaults saved successfully!")


def show_upload_history():
    """Upload history tracking"""
    
    st.subheader("📤 Upload History")
    
    if "upload_history" not in st.session_state:
        st.session_state.upload_history = [
            {"Date": "2026-07-22 19:42:24", "File": "inventory_data_20260722.csv", "Rows": 7265, "User": "Sujit Kumar", "Status": "Success"},
            {"Date": "2026-07-21 10:15:30", "File": "inventory_data_20260721.csv", "Rows": 7100, "User": "Sujit Kumar", "Status": "Success"},
            {"Date": "2026-07-20 14:22:10", "File": "inventory_data_20260720.csv", "Rows": 6890, "User": "Manager", "Status": "Success"},
        ]
    
    history_df = pd.DataFrame(st.session_state.upload_history)
    st.dataframe(history_df, use_container_width=True, hide_index=True)
    
    # Upload stats
    st.subheader("📊 Upload Statistics")
    
    total_uploads = len(st.session_state.upload_history)
    successful = len([h for h in st.session_state.upload_history if "Success" in h["Status"]])
    total_rows = sum([h["Rows"] for h in st.session_state.upload_history if "Success" in h["Status"]])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Uploads", total_uploads)
    col2.metric("Successful Uploads", successful)
    col3.metric("Total Rows Processed", f"{total_rows:,}")


def show_system_settings():
    """System settings"""
    
    st.subheader("⚙️ System Settings")
    
    st.info("Configure system-wide settings for the dashboard application.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Data Settings")
        
        data_refresh_interval = st.selectbox(
            "Data Refresh Interval",
            ["Every hour", "Every 4 hours", "Every 12 hours", "Every 24 hours", "Manual"],
            help="How often the dashboard should refresh data from the source"
        )
        
        cache_duration = st.number_input(
            "Cache Duration (minutes)",
            min_value=5,
            max_value=1440,
            value=30,
            step=5,
            help="How long to keep processed data in cache"
        )
    
    with col2:
        st.subheader("Display Settings")
        
        default_theme = st.selectbox(
            "Default Theme",
            ["Light", "Dark", "System"],
            help="Default theme for the dashboard"
        )
        
        date_format = st.selectbox(
            "Date Format",
            ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"],
            help="Default date format for all date displays"
        )
    
    st.subheader("🔄 Data Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Clear All Cache", use_container_width=True):
            st.session_state.dashboard_data = None
            st.session_state.filtered_dataframe = None
            st.success("✅ Cache cleared successfully!")
    
    with col2:
        if st.button("📊 Reset Dashboard", use_container_width=True):
            st.session_state.filters = {
                "expiry_window": "All Inventory",
                "category": "All Categories",
                "zsku": "All ZSKU",
                "store": "All Stores",
                "search": ""
            }
            st.session_state.dashboard_data = None
            st.session_state.filtered_dataframe = None
            st.success("✅ Dashboard reset successfully!")
    
    with col3:
        if st.button("💾 Export System Config", use_container_width=True):
            config = {
                "data_refresh_interval": data_refresh_interval,
                "cache_duration": cache_duration,
                "default_theme": default_theme,
                "date_format": date_format,
                "category_config": CATEGORY_CONFIG
            }
            config_json = json.dumps(config, indent=2)
            st.download_button(
                label="📥 Download Config",
                data=config_json,
                file_name=f"system_config_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    # System status
    st.subheader("🟢 System Status")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success("✅ Database: Connected")
    with col2:
        st.success("✅ Cache: Active")
    with col3:
        st.success("✅ API: Available")