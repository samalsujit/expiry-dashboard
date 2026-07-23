import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
import base64
from views.overview import render_filter_bar

# Consistent color palette
COLOR_SCALE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]


def show_reports():
    """Reports page - Generate ready-to-share business reports"""
    
    st.title("📄 Business Reports")
    
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
    summary = dashboard_data.get("summary", {})
    exceptions = dashboard_data.get("exceptions", {})
    
    if df.empty:
        st.warning("No data available. Please check your filters.")
        return
    
    # Get current filters for reporting
    current_filters = st.session_state.filters
    
    # ---------------- Report Type Selection ----------------
    st.subheader("📊 Select Report Type")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        report_type = st.selectbox(
            "Choose a report to generate:",
            [
                "Executive Summary",
                "Store Performance Report",
                "Category Performance Report",
                "Expiry Risk Report",
                "Exception Report",
                "Slow Moving Inventory Report",
                "Top 100 Products at Risk",
                "Full Data Export"
            ],
            help="Select the type of report you want to generate"
        )
    
    with col2:
        st.write("")
        st.write("")
        export_format = st.radio(
            "Export Format:",
            ["CSV", "Excel"],
            horizontal=True,
            help="Choose export format (Excel coming soon)"
        )
    
    st.divider()
    
    # ---------------- Generate Report Based on Selection ----------------
    if report_type == "Executive Summary":
        generate_executive_summary(df, summary, current_filters, export_format)
    elif report_type == "Store Performance Report":
        generate_store_report(df, current_filters, export_format)
    elif report_type == "Category Performance Report":
        generate_category_report(df, current_filters, export_format)
    elif report_type == "Expiry Risk Report":
        generate_expiry_report(df, current_filters, export_format)
    elif report_type == "Exception Report":
        generate_exception_report(df, exceptions, current_filters, export_format)
    elif report_type == "Slow Moving Inventory Report":
        generate_slow_moving_report(df, current_filters, export_format)
    elif report_type == "Top 100 Products at Risk":
        generate_top_risk_report(df, current_filters, export_format)
    elif report_type == "Full Data Export":
        generate_full_export(df, dashboard_data, current_filters, export_format)


def generate_executive_summary(df, summary, filters, export_format):
    """Generate executive summary report"""
    
    st.subheader("📋 Executive Summary")
    
    # Date and time
    now = datetime.now()
    st.caption(f"Generated on: {now.strftime('%B %d, %Y at %I:%M %p')}")
    
    # Show active filters
    if any(filters.get(k) not in ["All Inventory", "All Categories", "All ZSKU", "All Stores", ""] for k in filters.keys()):
        st.info(f"📌 Report filtered by: {', '.join([f'{k}: {v}' for k, v in filters.items() if v and v not in ['All Inventory', 'All Categories', 'All ZSKU', 'All Stores', '']])}")
    
    # ---------------- Key Insights ----------------
    st.markdown("### 💡 Key Insights (30-Second Read)")
    
    # Calculate insights
    if "days_to_expiry" in df.columns:
        expiring_7 = len(df[(df["days_to_expiry"] >= 0) & (df["days_to_expiry"] <= 7)])
        expiring_today = len(df[df["days_to_expiry"] == 0])
    else:
        expiring_7 = 0
        expiring_today = 0
    
    # Top category by value
    top_category = df.groupby("minutes_category_new")["value"].sum().idxmax() if not df.empty else "N/A"
    
    # Top store by value
    top_store = df.groupby("area_name_en")["value"].sum().idxmax() if not df.empty else "N/A"
    
    # Slow moving products
    from services.processor import build_low_drr_high_qty
    low_drr = build_low_drr_high_qty(df)
    slow_moving_count = len(low_drr)
    
    # Create insight cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 12px 16px;
            border-left: 4px solid #1f77b4;
            height: 100%;
        ">
            <div style="font-size: 11px; color: #6c757d; text-transform: uppercase;">Highest Value Category</div>
            <div style="font-size: 18px; font-weight: bold; margin-top: 4px;">{top_category}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 12px 16px;
            border-left: 4px solid #ff7f0e;
            height: 100%;
        ">
            <div style="font-size: 11px; color: #6c757d; text-transform: uppercase;">Highest Risk Store</div>
            <div style="font-size: 18px; font-weight: bold; margin-top: 4px;">{top_store}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 12px 16px;
            border-left: 4px solid #d62728;
            height: 100%;
        ">
            <div style="font-size: 11px; color: #6c757d; text-transform: uppercase;">Expiring in 7 Days</div>
            <div style="font-size: 18px; font-weight: bold; margin-top: 4px;">{expiring_7:,}</div>
            {f'<div style="font-size: 12px; color: #d62728;">⚠️ {expiring_today:,} expiring today</div>' if expiring_today > 0 else ''}
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 12px 16px;
            border-left: 4px solid #2ca02c;
            height: 100%;
        ">
            <div style="font-size: 11px; color: #6c757d; text-transform: uppercase;">Slow Moving Products</div>
            <div style="font-size: 18px; font-weight: bold; margin-top: 4px;">{slow_moving_count:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ---------------- KPIs ----------------
    st.markdown("### 📊 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Products", f"{summary['total_products']:,}")
    col2.metric("Total Quantity", f"{summary['total_quantity']:,}")
    col3.metric("Total Value", f"SAR {summary['total_value']:,.2f}")
    col4.metric("Stores", f"{summary['stores_affected']}")
    
    st.markdown("---")
    
    # ---------------- Expiry Summary ----------------
    st.markdown("### ⏰ Expiry Overview")
    
    if "days_to_expiry" in df.columns:
        # Get expiry buckets
        def get_expiry_bucket(days):
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
        
        df_expiry = df.copy()
        df_expiry["Expiry Bucket"] = df_expiry["days_to_expiry"].apply(get_expiry_bucket)
        
        expiry_summary = df_expiry.groupby("Expiry Bucket").agg({
            "zsku": "count",
            "qty": "sum",
            "value": "sum"
        }).reset_index()
        expiry_summary.columns = ["Bucket", "Products", "Quantity", "Value"]
        
        # Sort buckets
        bucket_order = ["Expired", "Today", "1-3 Days", "4-7 Days", "8-10 Days", "11-30 Days", "30+ Days"]
        expiry_summary["order"] = expiry_summary["Bucket"].apply(lambda x: bucket_order.index(x) if x in bucket_order else 999)
        expiry_summary = expiry_summary.sort_values("order").drop("order", axis=1)
        
        st.dataframe(expiry_summary, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # ---------------- Top Lists ----------------
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📂 Top 5 Categories by Value")
        top_categories = df.groupby("minutes_category_new")["value"].sum().sort_values(ascending=False).head(5)
        st.dataframe(top_categories.reset_index(), use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("### 🏪 Top 5 Stores by Value")
        top_stores = df.groupby("area_name_en")["value"].sum().sort_values(ascending=False).head(5)
        st.dataframe(top_stores.reset_index(), use_container_width=True, hide_index=True)
    
    # ---------------- Download ----------------
    st.markdown("---")
    if export_format == "CSV":
        download_report("Executive_Summary", df)
    else:
        st.info("📥 Excel export coming soon. CSV available now.")


def generate_store_report(df, filters, export_format):
    """Generate store performance report"""
    
    st.subheader("🏪 Store Performance Report")
    
    # Show active filters
    if any(filters.get(k) not in ["All Inventory", "All Categories", "All ZSKU", "All Stores", ""] for k in filters.keys()):
        st.info(f"📌 Report filtered by: {', '.join([f'{k}: {v}' for k, v in filters.items() if v and v not in ['All Inventory', 'All Categories', 'All ZSKU', 'All Stores', '']])}")
    
    store_summary = df.groupby("area_name_en").agg({
        "zsku": "count",
        "qty": "sum",
        "value": "sum",
        "days_to_expiry": "mean" if "days_to_expiry" in df.columns else lambda x: 0
    }).reset_index()
    
    store_summary.columns = ["Store", "Products", "Quantity", "Value", "Avg Days to Expiry"]
    store_summary = store_summary.sort_values("Value", ascending=False)
    
    # Calculate additional metrics
    store_summary["Avg Value per Product"] = store_summary["Value"] / store_summary["Products"]
    store_summary["% of Total Value"] = (store_summary["Value"] / store_summary["Value"].sum() * 100).round(1)
    
    # Display summary table
    st.dataframe(
        store_summary,
        use_container_width=True,
        hide_index=True,
        width="stretch"
    )
    
    # Top 10 stores chart
    st.subheader("Top 10 Stores by Value")
    fig = px.bar(
        store_summary.head(10),
        x="Store",
        y="Value",
        title="Store Performance",
        color="Value",
        color_continuous_scale="Blues",
        text="Value"
    )
    fig.update_traces(texttemplate='SAR %{text:,.0f}', textposition='outside')
    fig.update_layout(
        xaxis_title="Store",
        yaxis_title="Inventory Value (SAR)",
        showlegend=False,
        font=dict(family="Arial, sans-serif"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    if export_format == "CSV":
        download_report("Store_Performance", store_summary)
    else:
        st.info("📥 Excel export coming soon. CSV available now.")


def generate_category_report(df, filters, export_format):
    """Generate category performance report"""
    
    st.subheader("📂 Category Performance Report")
    
    # Show active filters
    if any(filters.get(k) not in ["All Inventory", "All Categories", "All ZSKU", "All Stores", ""] for k in filters.keys()):
        st.info(f"📌 Report filtered by: {', '.join([f'{k}: {v}' for k, v in filters.items() if v and v not in ['All Inventory', 'All Categories', 'All ZSKU', 'All Stores', '']])}")
    
    category_summary = df.groupby("minutes_category_new").agg({
        "zsku": "count",
        "qty": "sum",
        "value": "sum"
    }).reset_index()
    
    category_summary.columns = ["Category", "Products", "Quantity", "Value"]
    category_summary = category_summary.sort_values("Value", ascending=False)
    
    # Calculate additional metrics
    category_summary["Avg Value per Product"] = category_summary["Value"] / category_summary["Products"]
    category_summary["% of Total Value"] = (category_summary["Value"] / category_summary["Value"].sum() * 100).round(1)
    
    # Display summary table
    st.dataframe(
        category_summary,
        use_container_width=True,
        hide_index=True,
        width="stretch"
    )
    
    # Category distribution chart
    st.subheader("Category Value Distribution")
    fig = px.pie(
        category_summary.head(10),
        values="Value",
        names="Category",
        title="Top 10 Categories by Value",
        color_discrete_sequence=COLOR_SCALE
    )
    fig.update_layout(
        font=dict(family="Arial, sans-serif"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    if export_format == "CSV":
        download_report("Category_Performance", category_summary)
    else:
        st.info("📥 Excel export coming soon. CSV available now.")


def generate_expiry_report(df, filters, export_format):
    """Generate expiry risk report"""
    
    st.subheader("⏰ Expiry Risk Report")
    
    if "days_to_expiry" not in df.columns:
        st.warning("No expiry data available")
        return
    
    # Show active filters
    if any(filters.get(k) not in ["All Inventory", "All Categories", "All ZSKU", "All Stores", ""] for k in filters.keys()):
        st.info(f"📌 Report filtered by: {', '.join([f'{k}: {v}' for k, v in filters.items() if v and v not in ['All Inventory', 'All Categories', 'All ZSKU', 'All Stores', '']])}")
    
    # Create buckets
    def get_expiry_bucket(days):
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
    
    df_expiry = df.copy()
    df_expiry["Expiry Bucket"] = df_expiry["days_to_expiry"].apply(get_expiry_bucket)
    
    expiry_summary = df_expiry.groupby("Expiry Bucket").agg({
        "zsku": "count",
        "qty": "sum",
        "value": "sum"
    }).reset_index()
    expiry_summary.columns = ["Bucket", "Products", "Quantity", "Value"]
    
    # Sort buckets
    bucket_order = ["Expired", "Today", "1-3 Days", "4-7 Days", "8-10 Days", "11-30 Days", "30+ Days"]
    expiry_summary["order"] = expiry_summary["Bucket"].apply(lambda x: bucket_order.index(x) if x in bucket_order else 999)
    expiry_summary = expiry_summary.sort_values("order").drop("order", axis=1)
    
    # Calculate percentages
    total_value = expiry_summary["Value"].sum()
    expiry_summary["% of Value"] = (expiry_summary["Value"] / total_value * 100).round(1) if total_value > 0 else 0
    
    # Display summary
    st.dataframe(
        expiry_summary,
        use_container_width=True,
        hide_index=True,
        width="stretch"
    )
    
    # Expiry distribution chart
    st.subheader("Expiry Distribution")
    fig = px.bar(
        expiry_summary,
        x="Bucket",
        y="Value",
        title="Value at Risk by Expiry Bucket",
        color="Value",
        color_continuous_scale="RdYlGn_r",
        text="Value"
    )
    fig.update_traces(texttemplate='SAR %{text:,.0f}', textposition='outside')
    fig.update_layout(
        xaxis_title="Expiry Bucket",
        yaxis_title="Value at Risk (SAR)",
        showlegend=False,
        font=dict(family="Arial, sans-serif"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Products at risk table
    st.subheader("Products at Risk (Expiring in 30 Days)")
    risk_products = df[(df["days_to_expiry"] >= 0) & (df["days_to_expiry"] <= 30)].copy()
    risk_products = risk_products.sort_values("days_to_expiry", ascending=True)
    st.dataframe(
        risk_products[["zsku", "product_title", "days_to_expiry", "qty", "value", "area_name_en"]],
        use_container_width=True,
        hide_index=True,
        width="stretch"
    )
    
    if export_format == "CSV":
        download_report("Expiry_Risk", expiry_summary)
    else:
        st.info("📥 Excel export coming soon. CSV available now.")


def generate_exception_report(df, exceptions, filters, export_format):
    """Generate exception report"""
    
    st.subheader("⚠️ Exception Report")
    
    # Show active filters
    if any(filters.get(k) not in ["All Inventory", "All Categories", "All ZSKU", "All Stores", ""] for k in filters.keys()):
        st.info(f"📌 Report filtered by: {', '.join([f'{k}: {v}' for k, v in filters.items() if v and v not in ['All Inventory', 'All Categories', 'All ZSKU', 'All Stores', '']])}")
    
    null_expiry = exceptions.get("null_adjusted_expiry", pd.DataFrame())
    shelf_mismatch = exceptions.get("shelf_life_mismatch", pd.DataFrame())
    expiry_alerts = exceptions.get("expiry_disposal_alert", pd.DataFrame())
    low_drr = exceptions.get("low_drr_high_qty", pd.DataFrame())
    
    # Summary cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Null Adjusted Expiry", f"{len(null_expiry):,}")
    col2.metric("Shelf Life Mismatch", f"{len(shelf_mismatch):,}")
    col3.metric("Expiry Alerts", f"{len(expiry_alerts):,}")
    col4.metric("Low DRR", f"{len(low_drr):,}")
    
    # Show each exception type
    st.subheader("Exception Details")
    
    exception_tabs = st.tabs([
        f"Null Adjusted Expiry ({len(null_expiry)})",
        f"Shelf Life Mismatch ({len(shelf_mismatch)})",
        f"Expiry Alerts ({len(expiry_alerts)})",
        f"Low DRR ({len(low_drr)})"
    ])
    
    with exception_tabs[0]:
        if not null_expiry.empty:
            st.dataframe(null_expiry, use_container_width=True, hide_index=True, width="stretch")
        else:
            st.success("No exceptions found")
    
    with exception_tabs[1]:
        if not shelf_mismatch.empty:
            st.dataframe(shelf_mismatch, use_container_width=True, hide_index=True, width="stretch")
        else:
            st.success("No exceptions found")
    
    with exception_tabs[2]:
        if not expiry_alerts.empty:
            st.dataframe(expiry_alerts, use_container_width=True, hide_index=True, width="stretch")
        else:
            st.success("No exceptions found")
    
    with exception_tabs[3]:
        if not low_drr.empty:
            st.dataframe(low_drr, use_container_width=True, hide_index=True, width="stretch")
        else:
            st.success("No exceptions found")
    
    if export_format == "CSV":
        download_report("Exception_Report", pd.concat([null_expiry, shelf_mismatch, expiry_alerts, low_drr]))
    else:
        st.info("📥 Excel export coming soon. CSV available now.")


def generate_slow_moving_report(df, filters, export_format):
    """Generate slow moving inventory report"""
    
    st.subheader("🐢 Slow Moving Inventory Report")
    
    # Show active filters
    if any(filters.get(k) not in ["All Inventory", "All Categories", "All ZSKU", "All Stores", ""] for k in filters.keys()):
        st.info(f"📌 Report filtered by: {', '.join([f'{k}: {v}' for k, v in filters.items() if v and v not in ['All Inventory', 'All Categories', 'All ZSKU', 'All Stores', '']])}")
    
    from services.processor import build_low_drr_high_qty
    low_drr = build_low_drr_high_qty(df)
    
    if low_drr.empty:
        st.success("No slow moving products identified")
        return
    
    # Summary
    col1, col2, col3 = st.columns(3)
    col1.metric("Slow Moving Products", f"{len(low_drr):,}")
    col2.metric("Total Value", f"SAR {low_drr['value'].sum():,.2f}")
    col3.metric("Avg DRR", f"{low_drr['drr_max'].mean():.2f}")
    
    # Format ratio for display
    if "ratio" in low_drr.columns:
        low_drr["ratio_display"] = low_drr["ratio"].apply(
            lambda x: "N/A" if x == -1 else f"{x:.2f}"
        )
    
    # Show table
    st.dataframe(
        low_drr,
        use_container_width=True,
        hide_index=True,
        width="stretch"
    )
    
    # Distribution by reason
    reason_summary = low_drr.groupby("reason").size().reset_index(name="count")
    fig = px.pie(
        reason_summary,
        values="count",
        names="reason",
        title="Slow Moving Reasons",
        color_discrete_sequence=COLOR_SCALE
    )
    st.plotly_chart(fig, use_container_width=True)
    
    if export_format == "CSV":
        download_report("Slow_Moving_Inventory", low_drr)
    else:
        st.info("📥 Excel export coming soon. CSV available now.")


def generate_top_risk_report(df, filters, export_format):
    """Generate top 100 products at risk report"""
    
    st.subheader("🏆 Top 100 Products at Risk")
    
    if "days_to_expiry" not in df.columns:
        st.warning("No expiry data available")
        return
    
    # Show active filters
    if any(filters.get(k) not in ["All Inventory", "All Categories", "All ZSKU", "All Stores", ""] for k in filters.keys()):
        st.info(f"📌 Report filtered by: {', '.join([f'{k}: {v}' for k, v in filters.items() if v and v not in ['All Inventory', 'All Categories', 'All ZSKU', 'All Stores', '']])}")
    
    # Filter products with positive days to expiry
    risk_products = df[df["days_to_expiry"] >= 0].copy()
    
    # Create risk score
    risk_products["Risk Score"] = risk_products["value"] / (risk_products["days_to_expiry"] + 1)
    risk_products = risk_products.sort_values("Risk Score", ascending=False).head(100)
    
    # Display
    st.dataframe(
        risk_products[["zsku", "product_title", "days_to_expiry", "qty", "value", "Risk Score", "area_name_en"]],
        use_container_width=True,
        hide_index=True,
        width="stretch"
    )
    
    if export_format == "CSV":
        download_report("Top_100_Risk", risk_products)
    else:
        st.info("📥 Excel export coming soon. CSV available now.")


def generate_full_export(df, dashboard, filters, export_format):
    """Generate full data export"""
    
    st.subheader("📤 Full Data Export")
    
    # Show active filters
    if any(filters.get(k) not in ["All Inventory", "All Categories", "All ZSKU", "All Stores", ""] for k in filters.keys()):
        st.info(f"📌 Report filtered by: {', '.join([f'{k}: {v}' for k, v in filters.items() if v and v not in ['All Inventory', 'All Categories', 'All ZSKU', 'All Stores', '']])}")
    
    st.info("This report includes all processed data with all columns.")
    
    # Display data preview
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=400,
        width="stretch"
    )
    
    # Multiple export options
    if export_format == "CSV":
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"full_data_export_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("📥 Excel export coming soon. CSV available now.")


def download_report(name, data):
    """Helper function to download report data"""
    
    if isinstance(data, dict):
        data = pd.DataFrame(data)
    
    if not data.empty:
        csv = data.to_csv(index=False)
        st.download_button(
            label=f"📥 Download {name} (CSV)",
            data=csv,
            file_name=f"{name}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )