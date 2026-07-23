import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from views.overview import render_filter_bar

# Consistent color palette
COLOR_SCALE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]

# Severity levels with business priorities
SEVERITY_LEVELS = {
    "immediate": {"label": "🔴 Immediate Action", "color": "#d62728", "priority": 1},
    "action_3_days": {"label": "🟠 Action in 3 Days", "color": "#ff7f0e", "priority": 2},
    "monitor": {"label": "🟡 Monitor", "color": "#ffd93d", "priority": 3},
    "data_quality": {"label": "🔵 Data Quality", "color": "#17becf", "priority": 4},
}

# Action recommendations for each exception type
ACTION_RECOMMENDATIONS = {
    "null_adjusted_expiry": {
        "title": "📋 Null Adjusted Expiry",
        "recommendation": "Update adjusted expiry dates before stock take. Products without adjusted expiry cannot be properly tracked for disposal.",
        "priority": "data_quality"
    },
    "shelf_life_mismatch": {
        "title": "📋 Shelf Life Mismatch",
        "recommendation": "Verify master data. Shelf life doesn't match adjusted values. This may affect inventory planning and reorder points.",
        "priority": "data_quality"
    },
    "expiry_alerts": {
        "title": "🚨 Expiry Alerts",
        "recommendation": "Products expiring today. Immediate action required: remove from shelves, initiate disposal process, or run promotional offers.",
        "priority": "immediate"
    },
    "low_drr": {
        "title": "📦 Low DRR Products",
        "recommendation": "Slow moving inventory. Consider markdowns, transfer to higher-demand stores, or bundle with popular items.",
        "priority": "monitor"
    }
}


def show_exceptions():
    """Exceptions page - Action center for data quality issues"""
    
    st.title("⚠️ Exception Action Center")
    
    if "dashboard_data" not in st.session_state:
        st.info("Please upload data first.")
        return
    
    # Apply global filters from the filter bar
    filtered_df = render_filter_bar()
    
    if filtered_df is None or filtered_df.empty:
        st.warning("No data available. Please check your filters.")
        return
    
    # Reprocess with current filters
    from services.processor import process_dataframe
    expiry_window = st.session_state.filters.get("expiry_window", "All Inventory")
    dashboard_data = process_dataframe(filtered_df, expiry_window=expiry_window)
    
    df = dashboard_data.get("df", pd.DataFrame())
    exceptions = dashboard_data.get("exceptions", {})
    summary = dashboard_data.get("summary", {})
    
    if df.empty:
        st.warning("No data available. Please check your filters.")
        return
    
    # Get exception dataframes
    null_expiry = exceptions.get("null_adjusted_expiry", pd.DataFrame())
    shelf_mismatch = exceptions.get("shelf_life_mismatch", pd.DataFrame())
    expiry_alerts = exceptions.get("expiry_disposal_alert", pd.DataFrame())
    low_drr = exceptions.get("low_drr_high_qty", pd.DataFrame())
    
    # ---------------- Exception Health Score ----------------
    st.subheader("🏥 Exception Health Score")
    
    # Calculate health score
    total_products = summary.get("total_products", 1)
    total_exceptions = len(null_expiry) + len(shelf_mismatch) + len(expiry_alerts) + len(low_drr)
    
    # Calculate value at risk safely
    total_value_at_risk = (
        (null_expiry["value"].sum() if "value" in null_expiry.columns else 0)
        + (shelf_mismatch["value"].sum() if "value" in shelf_mismatch.columns else 0)
        + (expiry_alerts["value"].sum() if "value" in expiry_alerts.columns else 0)
        + (low_drr["value"].sum() if "value" in low_drr.columns else 0)
    )
    
    # Calculate health score (0-100)
    exception_rate = total_exceptions / total_products if total_products > 0 else 0
    value_risk_rate = total_value_at_risk / summary.get("total_value", 1) if summary.get("total_value", 0) > 0 else 0
    
    # Weighted score: 60% exception rate, 40% value risk
    health_score = max(0, 100 - (exception_rate * 50) - (value_risk_rate * 30))
    health_score = min(100, health_score)
    
    # Determine health status
    if health_score >= 90:
        status = "🟢 Excellent"
        status_color = "#2ca02c"
    elif health_score >= 75:
        status = "🟡 Good"
        status_color = "#ffd93d"
    elif health_score >= 60:
        status = "🟠 Attention Required"
        status_color = "#ff7f0e"
    else:
        status = "🔴 Critical"
        status_color = "#d62728"
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div style="
            background-color: #f8f9fa;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            border: 2px solid {status_color};
        ">
            <div style="font-size: 32px; font-weight: bold; color: {status_color};">
                {health_score:.0f}
            </div>
            <div style="font-size: 14px; color: #495057;">
                Health Score
            </div>
            <div style="font-size: 16px; font-weight: 600; color: {status_color};">
                {status}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.metric("🚨 Total Exceptions", f"{total_exceptions:,}")
    
    with col3:
        st.metric("💰 Value at Risk", f"SAR {total_value_at_risk:,.2f}")
    
    with col4:
        affected_stores = len(df["area_name_en"].unique()) if "area_name_en" in df.columns else 0
        st.metric("🏪 Affected Stores", f"{affected_stores:,}")
    
    with col5:
        affected_categories = len(df["minutes_category_new"].unique()) if "minutes_category_new" in df.columns else 0
        st.metric("📂 Affected Categories", f"{affected_categories:,}")
    
    st.divider()
    
    # ---------------- Exception Summary Cards ----------------
    st.subheader("📊 Exception Overview")
    
    # Create summary cards for each exception type
    exception_types = [
        ("Null Adjusted Expiry", len(null_expiry), null_expiry['value'].sum() if 'value' in null_expiry.columns else 0),
        ("Shelf Life Mismatch", len(shelf_mismatch), shelf_mismatch['value'].sum() if 'value' in shelf_mismatch.columns else 0),
        ("Expiry Alerts", len(expiry_alerts), expiry_alerts['value'].sum() if 'value' in expiry_alerts.columns else 0),
        ("Low DRR", len(low_drr), low_drr['value'].sum() if 'value' in low_drr.columns else 0),
    ]
    
    cols = st.columns(4)
    colors = ["#d62728", "#ff7f0e", "#ffd93d", "#17becf"]
    
    for idx, (name, count, value) in enumerate(exception_types):
        with cols[idx]:
            st.markdown(f"""
            <div style="
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 12px 16px;
                border-left: 4px solid {colors[idx]};
                margin-bottom: 8px;
            ">
                <div style="font-size: 12px; color: #6c757d;">{name}</div>
                <div style="font-size: 24px; font-weight: bold;">{count:,}</div>
                <div style="font-size: 12px; color: #6c757d;">SAR {value:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # ---------------- Exception Distribution Charts ----------------
    exception_df = pd.DataFrame(exception_types, columns=["Exception Type", "Count", "Value at Risk"])
    exception_df = exception_df[exception_df["Count"] > 0]
    
    if not exception_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(
                exception_df,
                x="Exception Type",
                y="Count",
                title="Exceptions by Type",
                color="Count",
                color_continuous_scale="OrRd",
                text="Count"
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(
                xaxis_title="Exception Type",
                yaxis_title="Number of Products",
                showlegend=False,
                font=dict(family="Arial, sans-serif"),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.pie(
                exception_df,
                values="Value at Risk",
                names="Exception Type",
                title="Value at Risk by Exception Type",
                color_discrete_sequence=COLOR_SCALE
            )
            fig.update_layout(
                font=dict(family="Arial, sans-serif"),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # ---------------- Exception Tabs with Recommendations ----------------
    st.subheader("🔍 Exception Details & Actions")
    
    # Create tabs with counts
    tab1, tab2, tab3, tab4 = st.tabs([
        f"📋 Null Adjusted Expiry ({len(null_expiry)})",
        f"📋 Shelf Life Mismatch ({len(shelf_mismatch)})",
        f"🚨 Expiry Alerts ({len(expiry_alerts)})",
        f"📦 Low DRR High Qty ({len(low_drr)})"
    ])
    
    with tab1:
        show_exception_table(
            null_expiry, 
            "null_adjusted_expiry",
            df
        )
    
    with tab2:
        show_exception_table(
            shelf_mismatch, 
            "shelf_life_mismatch",
            df
        )
    
    with tab3:
        show_exception_table(
            expiry_alerts, 
            "expiry_alerts",
            df,
            urgent=True
        )
    
    with tab4:
        show_exception_table(
            low_drr, 
            "low_drr",
            df
        )


def show_exception_table(data, exception_key, df, urgent=False):
    """Helper function to display exception tables with recommendations and actions"""
    
    if data.empty:
        st.success(f"✅ No {exception_key.replace('_', ' ').title()} exceptions found")
        return
    
    # Get recommendation
    rec = ACTION_RECOMMENDATIONS.get(exception_key, {})
    severity = SEVERITY_LEVELS.get(rec.get("priority", "data_quality"), {})
    
    # Display recommendation card
    st.markdown(f"""
    <div style="
        background-color: {'#fee' if severity.get('priority') == 1 else '#fff3cd' if severity.get('priority') == 3 else '#e7f5ff'};
        padding: 16px 20px;
        border-radius: 8px;
        border-left: 4px solid {severity.get('color', '#17becf')};
        margin-bottom: 16px;
    ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
            <div>
                <div style="font-weight: 600; font-size: 16px;">
                    {severity.get('label', 'ℹ️ Info')}
                </div>
                <div style="font-size: 14px; margin-top: 4px;">
                    {rec.get('recommendation', 'Review and take appropriate action.')}
                </div>
            </div>
            <div style="text-align: right; font-size: 13px; color: #6c757d;">
                <div>📊 {len(data)} products</div>
                <div>💰 SAR {data['value'].sum():,.2f} at risk</div>
                {f'<div style="color: #d62728; font-weight: 600;">🚨 Urgent</div>' if urgent else ''}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Filters for the exception table
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if "area_name_en" in data.columns:
            stores = ["All Stores"] + sorted(data["area_name_en"].dropna().unique().tolist())
            filter_store = st.selectbox("Filter by Store", stores, key=f"{exception_key}_store")
        else:
            filter_store = "All Stores"
    
    with col2:
        if "minutes_category_new" in data.columns:
            categories = ["All Categories"] + sorted(data["minutes_category_new"].dropna().unique().tolist())
            filter_category = st.selectbox("Filter by Category", categories, key=f"{exception_key}_category")
        else:
            filter_category = "All Categories"
    
    with col3:
        if "zsku" in data.columns:
            zskus = ["All ZSKU"] + sorted(data["zsku"].dropna().unique().tolist())
            filter_zsku = st.selectbox("Filter by ZSKU", zskus, key=f"{exception_key}_zsku")
        else:
            filter_zsku = "All ZSKU"
    
    # Apply filters
    filtered_data = data.copy()
    if filter_store != "All Stores":
        filtered_data = filtered_data[filtered_data["area_name_en"] == filter_store]
    if filter_category != "All Categories":
        filtered_data = filtered_data[filtered_data["minutes_category_new"] == filter_category]
    if filter_zsku != "All ZSKU":
        filtered_data = filtered_data[filtered_data["zsku"] == filter_zsku]
    
    # Reorder columns for better scanning
    column_order = [
        "area_name_en",      # Store
        "minutes_category_new",  # Category
        "zsku",              # ZSKU
        "product_title",     # Product
        "qty",               # Qty
        "value",             # Value
        "days_to_expiry",    # Days to Expiry
        "drr_max",           # DRR
        "reason",            # Reason
        "ratio_display",     # Ratio
    ]
    
    # Only include columns that exist
    display_columns = [col for col in column_order if col in filtered_data.columns]
    
    # Rename columns for display
    column_rename = {
        "area_name_en": "Store",
        "partner_warehouse_code": "Warehouse",
        "minutes_category_new": "Category",
        "zsku": "ZSKU",
        "product_title": "Product",
        "qty": "Qty",
        "value": "Value (SAR)",
        "days_to_expiry": "Days to Expiry",
        "drr_max": "DRR",
        "reason": "Reason",
        "ratio_display": "Ratio"
    }
    
    display_df = filtered_data[display_columns].rename(columns=column_rename)
    
    # Add severity column
    severity_label = SEVERITY_LEVELS.get(
        ACTION_RECOMMENDATIONS.get(exception_key, {}).get("priority", "data_quality"),
        {}
    ).get("label", "ℹ️ Info")
    
    display_df.insert(0, "Severity", severity_label)
    
    # Show the table
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        width="stretch"
    )
    
    # Action buttons with unique keys - FIXED: Added unique keys to each button
    st.subheader("📋 Actions")
    st.caption("Action buttons will be enabled in a future update with database integration")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.button(
            "📋 Assign", 
            disabled=True, 
            use_container_width=True, 
            help="Assign to team member (coming soon)",
            key=f"{exception_key}_assign"
        )
    with col2:
        st.button(
            "✅ Resolved", 
            disabled=True, 
            use_container_width=True, 
            help="Mark as resolved (coming soon)",
            key=f"{exception_key}_resolved"
        )
    with col3:
        st.button(
            "⏸️ Ignore", 
            disabled=True, 
            use_container_width=True, 
            help="Ignore exception (coming soon)",
            key=f"{exception_key}_ignore"
        )
    with col4:
        st.button(
            "⬆️ Escalate", 
            disabled=True, 
            use_container_width=True, 
            help="Escalate to manager (coming soon)",
            key=f"{exception_key}_escalate"
        )
    with col5:
        st.button(
            "📊 Details", 
            disabled=True, 
            use_container_width=True, 
            help="View product details (coming soon)",
            key=f"{exception_key}_details"
        )
    
    # Download button
    csv = filtered_data.to_csv(index=False)
    st.download_button(
        label=f"📥 Download {exception_key.replace('_', ' ').title()} Data (CSV)",
        data=csv,
        file_name=f"{exception_key}_{pd.Timestamp.today().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )