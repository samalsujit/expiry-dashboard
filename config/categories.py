# Category include/exclude configuration
CATEGORY_CONFIG = {
    "Beverages": "Include",
    "Bakery": "Exclude",
    "Dairy & Eggs": "Exclude",
    "Milk": "Exclude",
    "Rice, Pasta & Canned Food": "Include",
    "Chocolates, Candies & Biscuits": "Include",
    "Baby_Consumables": "Include",
    "Ready To Go": "Exclude",
    "Beauty": "Include",
    "Meat & Seafood": "Exclude",
    "Frozen": "Include",
    "Snacks": "Exclude",
    "Fruit & Vegetables": "Exclude",
    "Oils, Seasoning & Nuts": "Include",
    "Health & Wellness": "Include",
    "Baking & Sugars": "Exclude",
    "Icecream": "Exclude",
    "Personal Care": "Include",
    "Tea And Coffee": "Include",
    "Breakfast": "Exclude",
    "Household": "Include",
    "Pets": "Include",
}

def get_included_categories():
    """Get list of included categories"""
    return [cat for cat, status in CATEGORY_CONFIG.items() if status == "Include"]

def get_excluded_categories():
    """Get list of excluded categories"""
    return [cat for cat, status in CATEGORY_CONFIG.items() if status == "Exclude"]

def update_category_config(config):
    """Update category configuration"""
    global CATEGORY_CONFIG
    CATEGORY_CONFIG.update(config)