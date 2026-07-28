# views/overview.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from services.processor import process_dataframe, clean_dataframe

# Define a consistent color palette
COLOR_PALETTE = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "danger": "#d62728",
    "warning": "#ffd93d",
    "info": "#17becf",
    "purple": "#9467bd",
    "pink": "#e377c2",
    "brown": "#8c564b",
    "gray": "#7f7f7f",
    "teal": "#17becf"
}

COLOR_SCALE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]


def initialize_filters():
    """Initialize filter session state if not exists"""
    if "filters" not in st.session_state:
        st.session_state.filters = {
            "expiry_mode": "All Inventory",
            "exact_days": 0,
            "category": "All Categories",
            "zsku": "All ZSKU",
            "store": "All Stores",
            "search": ""
        }


def get_filtered_options(data, selected_category=None, selected_store=None):
    """Get filtered options for dependent dropdowns"""
    if data is None or data.empty:
        return pd.DataFrame()
    
    filtered_data = data.copy()
    
    if selected_category and selected_category != "All Categories":
        filtered_data = filtered_data[filtered_data["minutes_category_new"].astype(str) == str(selected_category)]
    
    if selected_store and selected_store != "All Stores":
        filtered_data = filtered_data[filtered_data["area_name_en"].astype(str) == str(selected_store)]
    
    return filtered_data


def apply_all_filters(data, filters):
    """Apply all filters to the dataframe"""
    if data is None or data.empty:
        return data
    
    filtered_data = data.copy()
    
    # Apply precise expiry mode filter
    expiry_mode = filters.get("expiry_mode", "All Inventory")
    if expiry_mode == "Expired (< 0 Days)":
        filtered_data = filtered_data[filtered_data["days_to_expiry"] < 0]
    elif expiry_mode == "Expiring Today (0 Days)":
        filtered_data = filtered_data[filtered_data["days_to_expiry"] == 0]
    elif expiry_mode == "Exact Days Ahead":
        exact_d = filters.get("exact_days", 0)
        filtered_data = filtered_data[filtered_data["days_to_expiry"] == exact_d]
    
    # Apply category filter
    if filters["category"] != "All Categories":
        filtered_data = filtered_data[filtered_data["minutes_category_new"].astype(str) == str(filters["category"])]
    
    # Apply store filter
    if filters["store"] != "All Stores":
        filtered_data = filtered_data[filtered_data["area_name_en"].astype(str) == str(filters["store"])]
    
    # Apply ZSKU filter
    if filters["zsku"] != "All ZSKU":
        filtered_data = filtered_data[filtered_data["zsku"].astype(str) == str(filters["zsku"])]
    
    # Apply search filter
    if filters["search"]:
        search_term = filters["search"].lower()
        filtered_data = filtered_data[
            filtered_data["zsku"].astype(str).str.lower().str.contains(search_term, na=False) |
            filtered_data["product_title"].astype(str).str.lower().str.contains(search_term, na=False) |
            filtered_data["barcode"].astype(str).str.lower().str.contains(search_term, na=False)
        ]
    
    return filtered_data


def render_filter_bar():
    """Render the production-grade filter bar with exact day offset selection"""
    
    df = st.session_state.get("original_dataframe")
    
    if df is None or df.empty:
        return None
    
    if "days_to_expiry" not in df.columns:
        df = clean_dataframe(df)
        st.session_state.original_dataframe = df
    
    initialize_filters()
    
    categories = sorted(df["minutes_category_new"].dropna().astype(str).unique())
    stores = sorted(df["area_name_en"].dropna().astype(str).unique())
    
    current_filters = st.session_state.filters
    
    zsku_options = ["All ZSKU"]
    filtered_for_zsku = get_filtered_options(
        df, 
        current_filters["category"], 
        current_filters["store"]
    )
    if not filtered_for_zsku.empty:
        zsku_options.extend(sorted(filtered_for_zsku["zsku"].dropna().astype(str).unique()))
    
    category_options = ["All Categories"]
    if current_filters["store"] != "All Stores":
        filtered_for_cat = df[df["area_name_en"].astype(str) == str(current_filters["store"])]
        category_options.extend(sorted(filtered_for_cat["minutes_category_new"].dropna().astype(str).unique()))
    else:
        category_options.extend(categories)
    
    store_options = ["All Stores"]
    if current_filters["category"] != "All Categories":
        filtered_for_store = df[df["minutes_category_new"].astype(str) == str(current_filters["category"])]
        store_options.extend(sorted(filtered_for_store["area_name_en"].dropna().astype(str).unique()))
    else:
        store_options.extend(stores)
    
    st.markdown("""
    <div style="
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid #e9ecef;
        margin-bottom: 16px;
    ">
        <div style="font-weight: 600; font-size: 0.9rem; color: #495057; margin-bottom: 8px;">
            🔍 Global Filters & Daily Expiry Targeting
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5, col6 = st.columns([2.2, 1.8, 1.8, 1.8, 1.5, 1])
    
    with col1:
        st.caption("📅 Expiry Selection")
        expiry_modes = ["All Inventory", "Expiring Today (0 Days)", "Expired (< 0 Days)", "Exact Days Ahead"]
        current_mode = current_filters.get("expiry_mode", "All Inventory")
        mode_index = expiry_modes.index(current_mode) if current_mode in expiry_modes else 0
        
        expiry_mode = st.selectbox(
            "Expiry Mode",
            options=expiry_modes,
            index=mode_index,
            key="filter_expiry_mode",
            label_visibility="collapsed"
        )
        current_filters["expiry_mode"] = expiry_mode
        
        # If Exact Days Ahead is selected, show a compact number input underneath
        if expiry_mode == "Exact Days Ahead":
            exact_days = st.number_input(
                "Days Ahead",
                min_value=0,
                max_value=365,
                value=current_filters.get("exact_days", 0),
                step=1,
                key="filter_exact_days"
            )
            current_filters["exact_days"] = exact_days
        else:
            current_filters["exact_days"] = 0
    
    with col2:
        st.caption("📂 Category")
        if current_filters["category"] not in category_options:
            current_filters["category"] = "All Categories"
        
        cat_index = category_options.index(current_filters["category"]) if current_filters["category"] in category_options else 0
        category = st.selectbox(
            "Category",
            options=category_options,
            index=cat_index,
            key="filter_category",
            label_visibility="collapsed"
        )
        current_filters["category"] = category
    
    with col3:
        st.caption("🔢 ZSKU")
        if current_filters["zsku"] not in zsku_options:
            current_filters["zsku"] = "All ZSKU"
        
        zsku_index = zsku_options.index(current_filters["zsku"]) if current_filters["zsku"] in zsku_options else 0
        zsku = st.selectbox(
            "ZSKU",
            options=zsku_options,
            index=zsku_index,
            key="filter_zsku",
            label_visibility="collapsed"
        )
        current_filters["zsku"] = zsku
    
    with col4:
        st.caption("🏪 Store")
        if current_filters["store"] not in store_options:
            current_filters["store"] = "All Stores"
        
        store_index = store_options.index(current_filters["store"]) if current_filters["store"] in store_options else 0
        store = st.selectbox(
            "Store",
            options=store_options,
            index=store_index,
            key="filter_store",
            label_visibility="collapsed"
        )
        current_filters["store"] = store
    
    with col5:
        st.caption("🔍 Search")
        search = st.text_input(
            "Search",
            value=current_filters["search"],
            key="filter_search",
            label_visibility="collapsed",
            placeholder="ZSKU, Product, Barcode..."
        )
        current_filters["search"] = search
    
    with col6:
        st.caption(" ")
        if st.button("🗑️ Clear", use_container_width=True, help="Reset all filters", key="clear_all_filters"):
            st.session_state.filters = {
                "expiry_mode": "All Inventory",
                "exact_days": 0,
                "category": "All Categories",
                "zsku": "All ZSKU",
                "store": "All Stores",
                "search": ""
            }
            
            for widget_key in ["filter_expiry_mode", "filter_exact_days", "filter_category", "filter_zsku", "filter_store", "filter_search"]:
                if widget_key in st.session_state:
                    del st.session_state[widget_key]
            
            st.rerun()
    
    active_filters = []
    filter_icons = {
        "expiry_mode": "📅",
        "category": "📂",
        "zsku": "🔢",
        "store": "🏪"
    }
    
    for key, value in current_filters.items():
        if key in ["search", "exact_days"]:
            continue
        if value and value not in ["All Categories", "All ZSKU", "All Stores", "All Inventory"]:
            icon = filter_icons.get(key, "")
            if key == "expiry_mode" and value == "Exact Days Ahead":
                active_filters.append(f"📅 Exactly {current_filters.get('exact_days', 0)} Days Ahead")
            else:
                active_filters.append(f"{icon} {value}")
    
    filtered_df = apply_all_filters(df, current_filters)
    
    expiring_today = len(filtered_df[filtered_df["days_to_expiry"] == 0]) if "days_to_expiry" in filtered_df.columns else 0
    avg_days_to_expiry = filtered_df["days_to_expiry"].mean() if "days_to_expiry" in filtered_df.columns and not filtered_df.empty else 0
    
    st.markdown("---")
    
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        total_qty = filtered_df['qty'].sum() if 'qty' in filtered_df.columns else 0
        st.metric("📊 Total Quantity", f"{total_qty:,.0f}")
    
    with col_b:
        if active_filters:
            st.write("**Active Filters:** " + " | ".join(active_filters))
        else:
            st.caption("All Inventory")
        if current_filters.get("search"):
            st.caption(f"🔍 Searching: \"{current_filters['search']}\"")
    
    col_c, col_d, col_e = st.columns(3)
    
    with col_c:
        st.metric("⏰ Avg Days to Expiry", f"{avg_days_to_expiry:.1f}")
    
    with col_d:
        color = "🔴" if expiring_today > 0 else "🟢"
        st.metric("🚨 Expiring Today", f"{color} {expiring_today}")
    
    with col_e:
        stores_count = filtered_df['area_name_en'].nunique() if 'area_name_en' in filtered_df.columns else 0
        st.metric("🏪 Stores Affected", f"{stores_count}")
    
    st.markdown("---")
    
    st.session_state.filtered_dataframe = filtered_df
    
    return filtered_df


def show_overview():
    """Main overview page with dashboard components"""
    
    df = st.session_state.get("original_dataframe")
    
    if df is None or df.empty:
        st.info("""
        📦 **No inventory data available**
        
        Please upload an inventory file from the **Upload** page to get started.
        """)
        
        if st.button("📤 Go to Upload", use_container_width=True):
            st.session_state.current_page = "upload"
            st.rerun()
        return
    
    filtered_df = render_filter_bar()
    
    if filtered_df is None or filtered_df.empty:
        st.warning("No records match the current filters. Please adjust your filters.")
        return
    
    with st.spinner("Updating dashboard..."):
        # Pass dummy window for processor compatibility
        dashboard_data = process_dataframe(filtered_df, expiry_window="All Inventory")
        st.session_state.dashboard_data = dashboard_data
    
    dashboard = st.session_state.dashboard_data
    summary = dashboard["summary"]

    st.divider()

    # ---------------- KPIs ----------------
    st.subheader("📈 Key Performance Indicators")
    
    expiring_today = len(filtered_df[filtered_df["days_to_expiry"] == 0]) if "days_to_expiry" in filtered_df.columns else 0
    avg_days = filtered_df["days_to_expiry"].mean() if "days_to_expiry" in filtered_df.columns and not filtered_df.empty else 0
    
    total_qty = filtered_df['qty'].sum() if 'qty' in filtered_df.columns else 0
    total_val = filtered_df['value'].sum() if 'value' in filtered_df.columns else 0
    stores_count = filtered_df['area_name_en'].nunique() if 'area_name_en' in filtered_df.columns else 0
    categories_count = filtered_df['minutes_category_new'].nunique() if 'minutes_category_new' in filtered_df.columns else 0

    val = total_val
    if val >= 1_000_000:
        val_str = f"SAR {val/1_000_000:.2f}M"
    elif val >= 1_000:
        val_str = f"SAR {val/1_000:.1f}K"
    else:
        val_str = f"SAR {val:,.2f}"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📂 Categories", f"{categories_count}")
    c2.metric("📊 Total Quantity", f"{total_qty:,.0f}")
    c3.metric("💰 Inventory Value", val_str)
    c4.metric("🏪 Stores Affected", f"{stores_count}")

    st.divider()

    # ---------------- ZSKU Lookup Expiry View ----------------
    current_filters = st.session_state.get("filters", {})
    if current_filters.get("zsku") != "All ZSKU" or current_filters.get("search") or current_filters.get("expiry_mode") == "Exact Days Ahead":
        st.subheader("🔍 Filtered Product Expiry & Batch Details")
        detail_cols = ["zsku", "product_title", "adjusted_expiry_date", "days_to_expiry", "qty", "value", "area_name_en"]
        available_detail_cols = [c for c in detail_cols if c in filtered_df.columns]
        st.dataframe(filtered_df[available_detail_cols], hide_index=True)
        st.divider()

    # ---------------- Expiry Summary with Chart ----------------
    st.subheader("⏰ Expiry Bucket Summary")
    
    if "days_to_expiry" in filtered_df.columns and not filtered_df.empty:
        def get_bucket(days):
            if days < 0: return "Expired"
            elif days == 0: return "Today"
            elif days <= 3: return "1-3 Days"
            elif days <= 7: return "4-7 Days"
            elif days <= 10: return "8-10 Days"
            elif days <= 30: return "11-30 Days"
            else: return "30+ Days"

        temp_df = filtered_df.copy()
        temp_df['Bucket'] = temp_df['days_to_expiry'].apply(get_bucket)
        
        bucket_agg = temp_df.groupby('Bucket').agg({'qty': 'sum', 'value': 'sum'}).reset_index()
        bucket_agg.columns = ['Bucket', 'Quantity', 'Value']
        
        all_buckets = ['Expired', 'Today', '1-3 Days', '4-7 Days', '8-10 Days', '11-30 Days', '30+ Days']
        expiry_df = pd.DataFrame({'Bucket': all_buckets})
        expiry_df = expiry_df.merge(bucket_agg, on='Bucket', how='left').fillna(0)
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            fig = px.bar(
                expiry_df,
                x='Bucket',
                y='Quantity',
                title='Inventory by Expiry Bucket',
                color='Quantity',
                color_continuous_scale='RdYlGn_r'
            )
            
            fig.update_layout(
                xaxis_title="Expiry Period", yaxis_title="Total Quantity",
                showlegend=False, font=dict(family="Arial, sans-serif"),
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.dataframe(expiry_df, hide_index=True)

    st.divider()

    # ---------------- Store Summary ----------------
    st.subheader("🏬 Store Summary")
    store_summary = dashboard["store_summary"]
    if not store_summary.empty:
        col1, col2 = st.columns([2, 1])
        with col1:
            top_stores = store_summary.head(10)
            fig = px.bar(
                top_stores, x='area_name_en', y='Value',
                title='Top 10 Stores by Inventory Value', color='Value', color_continuous_scale='Blues'
            )
            fig.update_layout(
                xaxis_title="Store", yaxis_title="Inventory Value (SAR)",
                showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.dataframe(store_summary, hide_index=True, height=400)
    else:
        st.info("No store data available for the selected filters")

    st.divider()

    # ---------------- Category Summary ----------------
    st.subheader("📂 Category Summary")
    category_summary = dashboard["category_summary"]
    if not category_summary.empty:
        col1, col2 = st.columns([2, 1])
        with col1:
            fig = px.pie(
                category_summary.head(10), values='Value', names='minutes_category_new',
                title='Category Distribution by Value', color_discrete_sequence=COLOR_SCALE
            )
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.dataframe(category_summary, hide_index=True, height=400)
    else:
        st.info("No category data available for the selected filters")

    st.divider()

    # ---------------- Top 10 ZSKU ----------------
    st.subheader("🏆 Top 10 ZSKU by Quantity")
    top10_zsku = dashboard["top10_zsku"]
    if not top10_zsku.empty:
        col1, col2 = st.columns([2, 1])
        with col1:
            fig = px.bar(
                top10_zsku, x='zsku', y='Quantity',
                title='Top 10 Products by Quantity', color='Value',
                color_continuous_scale='Viridis', hover_data=['product_title', 'Stores']
            )
            fig.update_layout(
                xaxis_title="ZSKU", yaxis_title="Quantity",
                showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.dataframe(top10_zsku, hide_index=True, height=400)
    else:
        st.info("No product data available for the selected filters")

    st.divider()

    # ---------------- Exception Alerts ----------------
    st.subheader("⚠️ Exception Alerts")
    exceptions = dashboard.get("exceptions", {})
    if exceptions:
        alert_tabs = st.tabs(["Null Adjusted Expiry", "Shelf Life Mismatch", "Expiry Disposal Alert", "Low DRR High Qty"])
        
        with alert_tabs[0]:
            null_expiry = exceptions.get("null_adjusted_expiry", pd.DataFrame())
            if not null_expiry.empty:
                st.dataframe(null_expiry, hide_index=True)
            else:
                st.success("✅ No products with null adjusted expiry date")
        
        with alert_tabs[1]:
            shelf_mismatch = exceptions.get("shelf_life_mismatch", pd.DataFrame())
            if not shelf_mismatch.empty:
                st.dataframe(shelf_mismatch, hide_index=True)
            else:
                st.success("✅ No shelf life mismatches found")
        
        with alert_tabs[2]:
            disposal_alerts = exceptions.get("expiry_disposal_alert", pd.DataFrame())
            if not disposal_alerts.empty:
                st.dataframe(disposal_alerts, hide_index=True)
            else:
                st.success("✅ No products expiring today")
        
        with alert_tabs[3]:
            low_drr = exceptions.get("low_drr_high_qty", pd.DataFrame())
            if not low_drr.empty:
                st.dataframe(low_drr, hide_index=True)
            else:
                st.success("✅ No products with low DRR and high quantity")
    else:
        st.info("No exception data available")

    st.divider()

    # ---------------- Raw Data ----------------
    with st.expander("📄 Processed Dataset"):
        df_data = dashboard.get("df", pd.DataFrame())
        if not df_data.empty:
            st.dataframe(df_data, hide_index=True, height=400)
            csv = df_data.to_csv(index=False)
            st.download_button(
                label="📥 Download Processed Data (CSV)",
                data=csv,
                file_name=f"processed_data_{dashboard.get('today', pd.Timestamp.today()).strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
