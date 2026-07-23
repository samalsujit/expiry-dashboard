# Role definitions
ROLES = {
    "Admin": {
        "permissions": ["all"],
        "pages": ["overview", "analytics", "forecast", "exceptions", "reports", "upload", "administration"],
        "description": "Full system access"
    },
    "Manager": {
        "permissions": ["view", "export", "upload"],
        "pages": ["overview", "analytics", "forecast", "exceptions", "reports", "upload"],
        "description": "Can view, export, and upload data"
    },
    "Analyst": {
        "permissions": ["view", "export"],
        "pages": ["overview", "analytics", "forecast", "exceptions", "reports"],
        "description": "Can view and export data"
    },
    "Viewer": {
        "permissions": ["view"],
        "pages": ["overview", "analytics", "forecast", "exceptions", "reports"],
        "description": "View-only access"
    }
}

# Admin users (email domains or specific emails)
ADMIN_USERS = [
    "susamal@noon.com",
    "admin@expiry-dashboard.com"
]

def is_admin(email):
    """Check if user is an admin"""
    return email in ADMIN_USERS

def get_user_role(email):
    """Get user role based on email"""
    if is_admin(email):
        return "Admin"
    return "Viewer"  # Default role

def get_user_pages(email):
    """Get accessible pages for a user"""
    role = get_user_role(email)
    return ROLES.get(role, {}).get("pages", [])