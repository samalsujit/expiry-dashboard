import streamlit as st
from services.processor import EXPIRY_WINDOWS, clean_dataframe


def render_global_filters():
    """Render the global filter bar - NO HTML, pure Streamlit"""
    
    # Check if data exists
    df = st.session_state.get("original_dataframe")
    if df is None or df.empty:
        return None
    
    # Ensure we have days_to_expiry
    if "days_to_expiry" not in df.columns:
        df = clean_dataframe(df)
        st.session_state.original_dataframe = df
    
    # Initialize filters
    if "filters" not in st.session_state:
        st.session_state.filters = {
            "expiry_window": "All Inventory",
            "category": "All Categories",
            "zsku": "All ZSKU",
            "store": "All Stores",
            "search": ""
        }
    
    filters = st.session_state.filters
    
    # Get options
    categories = sorted(df["minutes_category_new"].dropna().unique())
    stores = sorted(df["area_name_en"].dropna().unique())
    
    # Filter bar - Simple header
    st.subheader("🔍 Global Filters")
    
    # Filter row using columns
    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 1.5, 1])
    
    with col1:
        filters["expiry_window"] = st.selectbox(
            "📅 Expiry Window",
            options=list(EXPIRY_WINDOWS.keys()),
            index=list(EXPIRY_WINDOWS.keys()).index(filters["expiry_window"]),
            key="filter_expiry"
        )
    
    with col2:
        cat_options = ["All Categories"] + list(categories)
        if filters["category"] not in cat_options:
            filters["category"] = "All Categories"
        filters["category"] = st.selectbox(
            "📂 Category",
            options=cat_options,
            index=cat_options.index(filters["category"]) if filters["category"] in cat_options else 0,
            key="filter_category"
        )
    
    with col3:
        filtered_for_zsku = df.copy()
        if filters["category"] != "All Categories":
            filtered_for_zsku = filtered_for_zsku[filtered_for_zsku["minutes_category_new"] == filters["category"]]
        zsku_options = ["All ZSKU"] + sorted(filtered_for_zsku["zsku"].dropna().unique())
        if filters["zsku"] not in zsku_options:
            filters["zsku"] = "All ZSKU"
        filters["zsku"] = st.selectbox(
            "🔢 ZSKU",
            options=zsku_options,
            index=zsku_options.index(filters["zsku"]) if filters["zsku"] in zsku_options else 0,
            key="filter_zsku"
        )
    
    with col4:
        store_options = ["All Stores"] + list(stores)
        if filters["store"] not in store_options:
            filters["store"] = "All Stores"
        filters["store"] = st.selectbox(
            "🏪 Store",
            options=store_options,
            index=store_options.index(filters["store"]) if filters["store"] in store_options else 0,
            key="filter_store"
        )
    
    with col5:
        filters["search"] = st.text_input(
            "🔍 Search",
            value=filters["search"],
            key="filter_search",
            placeholder="ZSKU, Product..."
        )
    
    with col6:
        st.write("")  # Spacer
        if st.button("🗑️ Clear All", use_container_width=True, key="clear_filters"):
            st.session_state.filters = {
                "expiry_window": "All Inventory",
                "category": "All Categories",
                "zsku": "All ZSKU",
                "store": "All Stores",
                "search": ""
            }
            st.rerun()
    
    # Apply filters
    filtered_df = apply_filters(df, filters)
    
    # Stats bar - PURE STREAMLIT, NO HTML
    expiring_today = len(filtered_df[filtered_df["days_to_expiry"] == 0]) if "days_to_expiry" in filtered_df.columns else 0
    avg_days = filtered_df["days_to_expiry"].mean() if "days_to_expiry" in filtered_df.columns and not filtered_df.empty else 0
    
    # Build active filters display
    active_filters = []
    filter_icons = {"expiry_window": "📅", "category": "📂", "zsku": "🔢", "store": "🏪"}
    for key, value in filters.items():
        if key == "search":
            continue
        if value and value not in ["All Categories", "All ZSKU", "All Stores", "All Inventory"]:
            active_filters.append(f"{filter_icons.get(key, '')} {value}")
    
    # Display stats using columns - NO HTML
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Products", f"{len(filtered_df):,}")
    
    with col2:
        if active_filters:
            st.write("**Filters:** " + ", ".join(active_filters))
        else:
            st.write("**Filters:** All Inventory")
    
    with col3:
        st.metric("⏰ Avg Days", f"{avg_days:.1f}")
    
    with col4:
        st.metric("🚨 Expiring Today", f"{expiring_today}")
    
    st.markdown("---")
    
    st.session_state.filtered_dataframe = filtered_df
    return filtered_df


def apply_filters(df, filters):
    """Apply all filters to the dataframe"""
    if df is None or df.empty:
        return df
    
    filtered = df.copy()
    
    # Expiry window
    if filters["expiry_window"] != "All Inventory":
        if filters["expiry_window"] == "Expired":
            filtered = filtered[filtered["days_to_expiry"] < 0]
        else:
            window_range = EXPIRY_WINDOWS.get(filters["expiry_window"])
            if window_range:
                min_days, max_days = window_range
                filtered = filtered[
                    (filtered["days_to_expiry"] >= min_days) & 
                    (filtered["days_to_expiry"] <= max_days)
                ]
    
    # Category
    if filters["category"] != "All Categories":
        filtered = filtered[filtered["minutes_category_new"] == filters["category"]]
    
    # Store
    if filters["store"] != "All Stores":
        filtered = filtered[filtered["area_name_en"] == filters["store"]]
    
    # ZSKU
    if filters["zsku"] != "All ZSKU":
        filtered = filtered[filtered["zsku"] == filters["zsku"]]
    
    # Search
    if filters["search"]:
        search_term = filters["search"].lower()
        filtered = filtered[
            filtered["zsku"].str.lower().str.contains(search_term, na=False) |
            filtered["product_title"].str.lower().str.contains(search_term, na=False)
        ]
    
    return filtered


# Alias for backward compatibility
def render_filters():
    return render_global_filters()