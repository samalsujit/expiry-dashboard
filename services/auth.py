import streamlit as st
import re


class AuthService:
    """Authentication service for the application"""
    
    # Admin users
    ADMIN_USERS = [
        "susamal@noon.com",
        "admin@expiry-dashboard.com"
    ]
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def is_valid_domain(email, domain="noon.com"):
        """Check if email belongs to the allowed domain"""
        return email.lower().endswith(f"@{domain.lower()}")
    
    @staticmethod
    def get_user_role(email):
        """Get user role based on email"""
        if email.lower() in AuthService.ADMIN_USERS:
            return "Admin"
        elif AuthService.is_valid_domain(email):
            return "Manager"
        return "Viewer"
    
    @staticmethod
    def get_username(email):
        """Get display name from email"""
        if email.lower() == "susamal@noon.com":
            return "Sujit Kumar"
        return email.split("@")[0].title()
    
    @staticmethod
    def login(email):
        """Attempt to log in a user"""
        if not AuthService.validate_email(email):
            return {"success": False, "message": "Invalid email format"}
        
        if not AuthService.is_valid_domain(email):
            return {"success": False, "message": "Please use your @noon.com email address"}
        
        # Login successful
        return {
            "success": True,
            "username": AuthService.get_username(email),
            "role": AuthService.get_user_role(email),
            "email": email
        }
    
    @staticmethod
    def is_admin(email):
        """Check if user is an admin"""
        return email.lower() in AuthService.ADMIN_USERS
    
    @staticmethod
    def logout():
        """Log out the current user"""
        st.session_state.logged_in = False
        st.session_state.username = "Guest"
        st.session_state.user_role = "Viewer"
        st.session_state.user_email = ""
        return {"success": True}