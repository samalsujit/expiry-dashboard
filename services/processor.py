import pandas as pd
from datetime import datetime
import numpy as np

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

# Expiry window options
EXPIRY_WINDOWS = {
    "All Inventory": None,
    "Expired": (-999, -1),
    "Today": (0, 0),
    "Within 3 Days": (0, 3),
    "Within 7 Days": (0, 7),
    "Within 10 Days": (0, 10),
    "Within 30 Days": (0, 30),
}


def safe_int(value, default=0):
    if pd.isna(value):
        return default
    try:
        return int(float(value))
    except:
        return default


def safe_float(value, default=0.0):
    if pd.isna(value):
        return default
    try:
        return float(value)
    except:
        return default


def parse_date(value):
    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.date()

    if isinstance(value, datetime):
        return value.date()

    for fmt in (
        "%Y-%m-%d",
        "%b %d, %Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d-%m-%Y",
    ):
        try:
            return datetime.strptime(str(value), fmt).date()
        except:
            pass

    return None


def get_store_name(row):
    return str(row.get("area_name_en", "")).strip()


def get_category(row):
    return str(row.get("minutes_category_new", "")).strip()


def clean_dataframe(df):
    """Clean and prepare the dataframe with all necessary calculations"""
    data = df.copy()
    
    # Define optional columns with default values
    OPTIONAL_COLUMNS = {
        "drr_max": 0,
        "shelf_life": 0,
        "kl_adjusted": 0,
        "adjusted_expiry_date": pd.NaT,
        "barcode": "",
        "area_name_en": "",
        "partner_warehouse_code": "",
        "minutes_category_new": "",
        "product_title": "",
    }
    
    # Handle column name variations
    # KL_adjusted -> kl_adjusted
    if "KL_adjusted" in data.columns and "kl_adjusted" not in data.columns:
        data["kl_adjusted"] = data["KL_adjusted"]
    
    # pbarcode_canonical or wms_barcode -> barcode
    if "barcode" not in data.columns:
        if "pbarcode_canonical" in data.columns:
            data["barcode"] = data["pbarcode_canonical"]
        elif "wms_barcode" in data.columns:
            data["barcode"] = data["wms_barcode"]
        else:
            data["barcode"] = ""
    
    # Ensure all optional columns exist
    for col, default in OPTIONAL_COLUMNS.items():
        if col not in data.columns:
            data[col] = default
    
    # Convert numeric fields
    data["qty"] = (
        pd.to_numeric(
            data["qty"],
            errors="coerce"
        )
        .fillna(0)
        .astype(int)
    )

    data["cost_price"] = (
        pd.to_numeric(
            data["cost_price"],
            errors="coerce"
        )
        .fillna(0)
    )

    data["value"] = data["qty"] * data["cost_price"]

    # Normalize all numeric fields that downstream functions expect
    numeric_fields = ["drr_max", "shelf_life", "kl_adjusted"]
    for field in numeric_fields:
        data[field] = (
            pd.to_numeric(
                data[field],
                errors="coerce"
            )
            .fillna(0)
        )

    # Date fields
    data["expiry_date"] = pd.to_datetime(
        data["expiry_date"],
        errors="coerce"
    )

    data["adjusted_expiry_date"] = pd.to_datetime(
        data["adjusted_expiry_date"],
        errors="coerce"
    )

    today = pd.Timestamp.today().normalize()

    data["days_to_expiry"] = (
        data["expiry_date"] - today
    ).dt.days

    return data


def apply_category_filter(data):
    """Filter data to only include categories marked as 'Include'"""
    included = [
        cat
        for cat, status in CATEGORY_CONFIG.items()
        if status == "Include"
    ]

    return data[
        data["minutes_category_new"].isin(included)
    ].copy()


def build_summary(data):
    """Build KPI summary metrics"""
    return {
        "total_products": len(data),
        "total_quantity": int(data["qty"].sum()),
        "total_value": round(data["value"].sum(), 2),
        "stores_affected": data["area_name_en"].nunique(),
        "categories": data["minutes_category_new"].nunique(),
        "zsku": data["zsku"].nunique()
    }


def build_store_summary(data):
    """Build store-level summary aggregation"""
    return (
        data.groupby(
            ["area_name_en", "partner_warehouse_code"],
            as_index=False
        )
        .agg(
            Products=("zsku", "count"),
            Quantity=("qty", "sum"),
            Value=("value", "sum")
        )
        .sort_values("Value", ascending=False)
    )


def build_category_summary(data):
    """Build category-level summary aggregation"""
    return (
        data.groupby(
            "minutes_category_new",
            as_index=False
        )
        .agg(
            Products=("zsku", "count"),
            Quantity=("qty", "sum"),
            Value=("value", "sum")
        )
        .sort_values("Value", ascending=False)
    )


def build_top10_zsku(data):
    """Build top 10 ZSKU by quantity"""
    return (
        data.groupby(
            ["zsku", "product_title", "minutes_category_new"],
            as_index=False
        )
        .agg(
            Quantity=("qty", "sum"),
            Value=("value", "sum"),
            Stores=("area_name_en", "nunique")
        )
        .sort_values("Quantity", ascending=False)
        .head(10)
    )


def get_expiry_bucket(days):
    """Return the expiry bucket for a given number of days"""
    if pd.isna(days):
        return "Unknown"
    
    if days < 0:
        return "Expired"
    elif days == 0:
        return "Today"
    elif days <= 3:
        return "1-3 Days"
    elif days <= 7:
        return "4-7 Days"
    elif days <= 10:
        return "8-10 Days"
    elif days <= 30:
        return "11-30 Days"
    else:
        return "30+ Days"


def build_expiry_summary(data):
    """Build expiry bucket summary - quantity only as per original dashboard"""
    data = data.copy()
    
    # Initialize buckets with 0
    expiry_buckets = {
        'expired': 0,
        'today': 0,
        'days1_3': 0,
        'days4_7': 0,
        'days8_10': 0,
        'days11_30': 0,
        'days31plus': 0
    }
    
    # Populate buckets with quantities using vectorized operations for performance
    mask_expired = data['days_to_expiry'] < 0
    mask_today = data['days_to_expiry'] == 0
    mask_1_3 = (data['days_to_expiry'] > 0) & (data['days_to_expiry'] <= 3)
    mask_4_7 = (data['days_to_expiry'] > 3) & (data['days_to_expiry'] <= 7)
    mask_8_10 = (data['days_to_expiry'] > 7) & (data['days_to_expiry'] <= 10)
    mask_11_30 = (data['days_to_expiry'] > 10) & (data['days_to_expiry'] <= 30)
    mask_31plus = data['days_to_expiry'] > 30
    
    expiry_buckets['expired'] = data.loc[mask_expired, 'qty'].sum()
    expiry_buckets['today'] = data.loc[mask_today, 'qty'].sum()
    expiry_buckets['days1_3'] = data.loc[mask_1_3, 'qty'].sum()
    expiry_buckets['days4_7'] = data.loc[mask_4_7, 'qty'].sum()
    expiry_buckets['days8_10'] = data.loc[mask_8_10, 'qty'].sum()
    expiry_buckets['days11_30'] = data.loc[mask_11_30, 'qty'].sum()
    expiry_buckets['days31plus'] = data.loc[mask_31plus, 'qty'].sum()
    
    return expiry_buckets


def build_null_adjusted_expiry(data):
    """Find products with null adjusted expiry date"""
    if data.empty:
        return pd.DataFrame()
    
    result = data[data["adjusted_expiry_date"].isna()][[
        "zsku", 
        "product_title", 
        "area_name_en",
        "partner_warehouse_code",
        "minutes_category_new",
        "qty",
        "value",
        "drr_max",
        "shelf_life",
        "kl_adjusted",
        "barcode",
        "cost_price",
        "expiry_date", 
        "adjusted_expiry_date"
    ]].drop_duplicates()
    
    return result


def build_shelf_life_mismatch(data):
    """Find products where shelf_life == kl_adjusted (preserving original business logic)"""
    if data.empty:
        return pd.DataFrame()
    
    result = data[data["shelf_life"] == data["kl_adjusted"]][[
        "zsku", 
        "product_title", 
        "area_name_en",
        "partner_warehouse_code",
        "minutes_category_new",
        "qty",
        "value",
        "drr_max",
        "shelf_life",
        "kl_adjusted",
        "barcode",
        "cost_price"
    ]].drop_duplicates()
    
    return result


def build_expiry_disposal_alert(data):
    """Find products expiring today (days_to_expiry == 0 as per original dashboard)"""
    if data.empty:
        return pd.DataFrame()
    
    result = data[data["days_to_expiry"] == 0][[
        "zsku", 
        "product_title", 
        "area_name_en",
        "partner_warehouse_code",
        "minutes_category_new",
        "qty",
        "value",
        "drr_max",
        "shelf_life",
        "kl_adjusted",
        "barcode",
        "cost_price",
        "expiry_date", 
        "days_to_expiry"
    ]].sort_values("days_to_expiry", ascending=True)
    
    return result


def build_low_drr_high_qty(data):
    """Find products with low DRR and high quantity (exact original dashboard logic)"""
    if data.empty:
        return pd.DataFrame()
    
    result = []
    
    for _, row in data.iterrows():
        drr_max = row.get('drr_max', 0)
        qty = row.get('qty', 0)
        
        # Calculate ratio (original dashboard logic)
        # Store as float for Arrow compatibility, use -1 for "N/A"
        if drr_max == 0:
            ratio = -1.0  # Use -1 to represent "N/A" for display later
        else:
            ratio = qty / drr_max
        
        # Apply rules (only flag products that actually have stock)
        if drr_max == 0 and qty > 0:
            result.append({
                'zsku': row.get('zsku', ''),
                'product_title': row.get('product_title', ''),
                'area_name_en': row.get('area_name_en', ''),
                'partner_warehouse_code': row.get('partner_warehouse_code', ''),
                'minutes_category_new': row.get('minutes_category_new', ''),
                'qty': qty,
                'value': row.get('value', 0),
                'drr_max': drr_max,
                'shelf_life': row.get('shelf_life', 0),
                'kl_adjusted': row.get('kl_adjusted', 0),
                'barcode': row.get('barcode', ''),
                'cost_price': row.get('cost_price', 0),
                'ratio': ratio,  # Now a float, Arrow compatible
                'reason': 'Zero DRR'
            })
        elif drr_max <= 2 and qty > 0:
            result.append({
                'zsku': row.get('zsku', ''),
                'product_title': row.get('product_title', ''),
                'area_name_en': row.get('area_name_en', ''),
                'partner_warehouse_code': row.get('partner_warehouse_code', ''),
                'minutes_category_new': row.get('minutes_category_new', ''),
                'qty': qty,
                'value': row.get('value', 0),
                'drr_max': drr_max,
                'shelf_life': row.get('shelf_life', 0),
                'kl_adjusted': row.get('kl_adjusted', 0),
                'barcode': row.get('barcode', ''),
                'cost_price': row.get('cost_price', 0),
                'ratio': ratio,  # Now a float, Arrow compatible
                'reason': 'DRR <= 2'
            })
        elif drr_max < 5 and qty > 10:
            result.append({
                'zsku': row.get('zsku', ''),
                'product_title': row.get('product_title', ''),
                'area_name_en': row.get('area_name_en', ''),
                'partner_warehouse_code': row.get('partner_warehouse_code', ''),
                'minutes_category_new': row.get('minutes_category_new', ''),
                'qty': qty,
                'value': row.get('value', 0),
                'drr_max': drr_max,
                'shelf_life': row.get('shelf_life', 0),
                'kl_adjusted': row.get('kl_adjusted', 0),
                'barcode': row.get('barcode', ''),
                'cost_price': row.get('cost_price', 0),
                'ratio': ratio,  # Now a float, Arrow compatible
                'reason': 'DRR < 5 and Qty > 10'
            })
        elif drr_max < 10 and qty > 30:
            result.append({
                'zsku': row.get('zsku', ''),
                'product_title': row.get('product_title', ''),
                'area_name_en': row.get('area_name_en', ''),
                'partner_warehouse_code': row.get('partner_warehouse_code', ''),
                'minutes_category_new': row.get('minutes_category_new', ''),
                'qty': qty,
                'value': row.get('value', 0),
                'drr_max': drr_max,
                'shelf_life': row.get('shelf_life', 0),
                'kl_adjusted': row.get('kl_adjusted', 0),
                'barcode': row.get('barcode', ''),
                'cost_price': row.get('cost_price', 0),
                'ratio': ratio,  # Now a float, Arrow compatible
                'reason': 'DRR < 10 and Qty > 30'
            })
    
    result_df = pd.DataFrame(result)
    
    # Convert ratio back to "N/A" for display (but keep as float in dataframe)
    # We'll handle display formatting in the UI
    return result_df


def process_dataframe(df, expiry_window="All Inventory"):
    """Main processing function that orchestrates all data transformations"""
    if df.empty:
        return {}
    
    # Clean data
    data = clean_dataframe(df)
    
    # Apply category filter
    data = apply_category_filter(data)
    
    # Apply expiry window filter (only if data has days_to_expiry)
    if "days_to_expiry" in data.columns:
        if expiry_window != "All Inventory":
            if expiry_window == "Expired":
                data = data[data["days_to_expiry"] < 0]
            else:
                window_range = EXPIRY_WINDOWS.get(expiry_window)
                if window_range:
                    min_days, max_days = window_range
                    data = data[
                        (data["days_to_expiry"] >= min_days) & 
                        (data["days_to_expiry"] <= max_days)
                    ]
    
    # Get reference date once for the entire dashboard
    today = pd.Timestamp.today().normalize()
    
    # Build all summaries
    summary = build_summary(data)
    store_summary = build_store_summary(data)
    category_summary = build_category_summary(data)
    top10_zsku = build_top10_zsku(data)
    expiry_summary = build_expiry_summary(data)
    
    # Build exception tables (migrated from original dashboard)
    null_adjusted_expiry = build_null_adjusted_expiry(data)
    shelf_life_mismatch = build_shelf_life_mismatch(data)
    expiry_disposal_alert = build_expiry_disposal_alert(data)
    low_drr_high_qty = build_low_drr_high_qty(data)
    
    return {
        "df": data,
        "summary": summary,
        "store_summary": store_summary,
        "category_summary": category_summary,
        "top10_zsku": top10_zsku,
        "expiry_summary": expiry_summary,
        "exceptions": {
            "null_adjusted_expiry": null_adjusted_expiry,
            "shelf_life_mismatch": shelf_life_mismatch,
            "expiry_disposal_alert": expiry_disposal_alert,
            "low_drr_high_qty": low_drr_high_qty
        },
        "today": today,
        "expiry_window": expiry_window
    }