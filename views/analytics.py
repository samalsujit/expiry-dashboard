import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from services.processor import build_low_drr_high_qty

# Consistent color palette
COLOR_SCALE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]


def show_analytics():
    """Analytics page with deep insights into inventory data"""
    
    st.title("📊 Inventory Analytics")
    
    if "dashboard_data" not in st.session_state:
        st.info("Please upload data first.")
        return
    
    # Use the existing dashboard_data to avoid reprocessing
    dashboard = st.session_state.dashboard_data
    df = dashboard.get("df", pd.DataFrame())
    
    if df.empty:
        st.warning("No data available. Please check your filters.")
        return
    
    summary = dashboard["summary"]
    
    # ---------------- Quick Stats ----------------
    st.subheader("📈 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Products", f"{summary['total_products']:,}")
    col2.metric("Total Quantity", f"{summary['total_quantity']:,}")
    col3.metric("Total Value", f"SAR {summary['total_value']:,.2f}")
    col4.metric("Categories", f"{summary['categories']}")
    
    st.divider()
    
    # ---------------- Treemap: Value by Category & Store ----------------
    st.subheader("🏷️ Inventory Value by Category")
    
    # Create hierarchical treemap: Category -> Store -> Value
    category_store_value = df.groupby(["minutes_category_new", "area_name_en"])["value"].sum().reset_index()
    
    if not category_store_value.empty:
        fig = px.treemap(
            category_store_value,
            path=['minutes_category_new', 'area_name_en'],
            values='value',
            title='Value Distribution by Category and Store',
            color='value',
            color_continuous_scale='Blues',
            hover_data={'value': ':,.2f'}
        )
        fig.update_layout(
            font=dict(family="Arial, sans-serif"),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category data available")
    
    st.divider()
    
    # ---------------- Two-Column Layout: Store + Aging ----------------
    col1, col2 = st.columns(2)
    
    with col1:
        # ---------------- Store Rankings ----------------
        st.subheader("🏪 Top 20 Stores by Value")
        
        store_value = df.groupby(["area_name_en"])["value"].sum().reset_index()
        store_value = store_value.sort_values("value", ascending=False)
        
        if not store_value.empty:
            top_stores = store_value.head(20)
            fig = px.bar(
                top_stores,
                x='area_name_en',
                y='value',
                title='Top 20 Stores by Inventory Value',
                color='value',
                color_continuous_scale='Reds',
                text='value'
            )
            fig.update_traces(texttemplate='SAR %{text:,.0f}', textposition='outside')
            fig.update_layout(
                xaxis_title="Store",
                yaxis_title="Inventory Value (SAR)",
                showlegend=False,
                font=dict(family="Arial, sans-serif"),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No store data available")
    
    with col2:
        # ---------------- Inventory Aging ----------------
        st.subheader("⏳ Inventory Aging Analysis")
        
        if "days_to_expiry" in df.columns:
            # Create aging buckets
            def get_aging_bucket(days):
                if pd.isna(days):
                    return "Unknown"
                if days < 0:
                    return "Expired"
                elif days <= 7:
                    return "0-7 Days"
                elif days <= 15:
                    return "8-15 Days"
                elif days <= 30:
                    return "16-30 Days"
                elif days <= 60:
                    return "31-60 Days"
                else:
                    return "60+ Days"
            
            df_aging = df.copy()
            df_aging['aging_bucket'] = df_aging['days_to_expiry'].apply(get_aging_bucket)
            
            aging_summary = df_aging.groupby('aging_bucket').agg({
                'zsku': 'count',
                'qty': 'sum',
                'value': 'sum'
            }).reset_index()
            aging_summary.columns = ['Bucket', 'Products', 'Quantity', 'Value']
            
            # Calculate percentages
            total_value = aging_summary['Value'].sum()
            total_qty = aging_summary['Quantity'].sum()
            aging_summary['% of Value'] = (aging_summary['Value'] / total_value * 100).round(1) if total_value > 0 else 0
            aging_summary['% of Quantity'] = (aging_summary['Quantity'] / total_qty * 100).round(1) if total_qty > 0 else 0
            
            # Sort buckets in logical order
            bucket_order = ['Expired', '0-7 Days', '8-15 Days', '16-30 Days', '31-60 Days', '60+ Days', 'Unknown']
            aging_summary['order'] = aging_summary['Bucket'].apply(lambda x: bucket_order.index(x) if x in bucket_order else 999)
            aging_summary = aging_summary.sort_values('order').drop('order', axis=1)
            
            # Bar chart for aging
            fig = px.bar(
                aging_summary,
                x='Bucket',
                y='Value',
                title='Inventory Value by Aging Bucket',
                color='Value',
                color_continuous_scale='RdYlGn_r',
                text='Value'
            )
            fig.update_traces(texttemplate='SAR %{text:,.0f}', textposition='outside')
            fig.update_layout(
                xaxis_title="Aging Bucket",
                yaxis_title="Inventory Value (SAR)",
                showlegend=False,
                font=dict(family="Arial, sans-serif"),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show aging table with percentages
            with st.expander("📋 Aging Details with Percentages"):
                st.dataframe(
                    aging_summary,
                    use_container_width=True,
                    hide_index=True,
                )
        else:
            st.info("No aging data available")
    
    st.divider()
    
    # ---------------- Two-Column Layout: Expiry Distribution + Product Distribution ----------------
    col1, col2 = st.columns(2)
    
    with col1:
        # ---------------- Expiry Distribution ----------------
        st.subheader("📊 Expiry Distribution")
        
        if "days_to_expiry" in df.columns:
            # Add toggle for metric type
            metric_type = st.radio(
                "Display:",
                ["Product Count", "Inventory Value", "Quantity"],
                horizontal=True,
                key="expiry_metric"
            )
            
            # Map metric to column
            metric_map = {
                "Product Count": "count",
                "Inventory Value": "value",
                "Quantity": "qty"
            }
            
            # Create histogram based on selected metric
            if metric_type == "Product Count":
                fig = px.histogram(
                    df,
                    x='days_to_expiry',
                    nbins=50,
                    title='Distribution of Days to Expiry',
                    color_discrete_sequence=['#1f77b4'],
                    labels={'days_to_expiry': 'Days to Expiry', 'count': 'Number of Products'}
                )
            elif metric_type == "Inventory Value":
                # Group by days and sum value
                df_expiry = df.groupby(pd.cut(df['days_to_expiry'], bins=50))['value'].sum().reset_index()
                df_expiry['days_to_expiry'] = df_expiry['days_to_expiry'].apply(lambda x: x.mid)
                fig = px.bar(
                    df_expiry,
                    x='days_to_expiry',
                    y='value',
                    title='Inventory Value by Days to Expiry',
                    color_discrete_sequence=['#2ca02c'],
                    labels={'days_to_expiry': 'Days to Expiry', 'value': 'Inventory Value (SAR)'}
                )
            else:  # Quantity
                df_expiry = df.groupby(pd.cut(df['days_to_expiry'], bins=50))['qty'].sum().reset_index()
                df_expiry['days_to_expiry'] = df_expiry['days_to_expiry'].apply(lambda x: x.mid)
                fig = px.bar(
                    df_expiry,
                    x='days_to_expiry',
                    y='qty',
                    title='Quantity by Days to Expiry',
                    color_discrete_sequence=['#ff7f0e'],
                    labels={'days_to_expiry': 'Days to Expiry', 'qty': 'Total Quantity'}
                )
            
            # Add vertical lines for key thresholds
            fig.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Expired")
            fig.add_vline(x=7, line_dash="dash", line_color="orange", annotation_text="7 Days")
            fig.add_vline(x=30, line_dash="dash", line_color="green", annotation_text="30 Days")
            
            fig.update_layout(
                font=dict(family="Arial, sans-serif"),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                bargap=0.1,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Quick stats
            expiring_7 = len(df[(df['days_to_expiry'] >= 0) & (df['days_to_expiry'] <= 7)])
            expiring_30 = len(df[(df['days_to_expiry'] >= 0) & (df['days_to_expiry'] <= 30)])
            
            col_a, col_b = st.columns(2)
            col_a.metric("Expiring ≤ 7 Days", f"{expiring_7:,}")
            col_b.metric("Expiring ≤ 30 Days", f"{expiring_30:,}")
        else:
            st.info("No expiry data available")
    
    with col2:
        # ---------------- Product Distribution ----------------
        st.subheader("📦 Product Distribution")
        
        if len(df['minutes_category_new'].unique()) > 1:
            # Add toggle for metric type
            dist_metric = st.radio(
                "Display:",
                ["Quantity", "Value"],
                horizontal=True,
                key="dist_metric"
            )
            
            if dist_metric == "Quantity":
                fig = px.box(
                    df,
                    x='minutes_category_new',
                    y='qty',
                    title='Quantity Distribution by Category',
                    color='minutes_category_new',
                    color_discrete_sequence=COLOR_SCALE,
                    labels={'qty': 'Quantity', 'minutes_category_new': 'Category'}
                )
            else:
                fig = px.box(
                    df,
                    x='minutes_category_new',
                    y='value',
                    title='Value Distribution by Category',
                    color='minutes_category_new',
                    color_discrete_sequence=COLOR_SCALE,
                    labels={'value': 'Inventory Value (SAR)', 'minutes_category_new': 'Category'}
                )
            
            fig.update_layout(
                showlegend=False,
                font=dict(family="Arial, sans-serif"),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_tickangle=-45,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show category summary
            category_summary = df.groupby('minutes_category_new').agg({
                'qty': 'sum',
                'value': 'sum',
                'zsku': 'count'
            }).reset_index()
            category_summary.columns = ['Category', 'Total Quantity', 'Total Value', 'Product Count']
            category_summary = category_summary.sort_values('Total Value', ascending=False)
            
            with st.expander("📋 Category Summary"):
                st.dataframe(
                    category_summary,
                    use_container_width=True,
                    hide_index=True,
                )
        else:
            st.info("Need multiple categories for box plot")
    
    st.divider()
    
    # ---------------- Slow Moving Products ----------------
    st.subheader("🐢 Slow Moving Products (Low DRR)")
    
    # Calculate total value of slow moving products
    low_drr_df = build_low_drr_high_qty(df)
    
    if not low_drr_df.empty:
        total_slow_value = low_drr_df['value'].sum() if 'value' in low_drr_df.columns else 0
        total_inventory_value = summary['total_value']
        slow_percentage = (total_slow_value / total_inventory_value * 100) if total_inventory_value > 0 else 0
        
        # Display prominent metrics
        col1, col2, col3 = st.columns(3)
        col1.metric(
            "Slow Moving Products",
            f"{len(low_drr_df):,}",
            delta=f"{slow_percentage:.1f}% of total value"
        )
        col2.metric(
            "Total Value at Risk",
            f"SAR {total_slow_value:,.2f}"
        )
        col3.metric(
            "Avg DRR",
            f"{low_drr_df['drr_max'].mean():.2f}" if 'drr_max' in low_drr_df.columns else "N/A"
        )
        
        # Format ratio for display
        if "ratio" in low_drr_df.columns:
            low_drr_df["ratio_display"] = low_drr_df["ratio"].apply(
                lambda x: "N/A" if x == -1 else f"{x:.2f}"
            )
        
        # Show summary by reason
        reason_summary = low_drr_df.groupby('reason').size().reset_index(name='count')
        reason_summary = reason_summary.sort_values('count', ascending=False)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.dataframe(
                reason_summary,
                use_container_width=True,
                hide_index=True,
            )
        
        with col2:
            fig = px.pie(
                reason_summary,
                values='count',
                names='reason',
                title='Slow Moving Products by Reason',
                color_discrete_sequence=COLOR_SCALE
            )
            fig.update_layout(
                font=dict(family="Arial, sans-serif"),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Full list
        with st.expander("📋 Full List of Slow Moving Products"):
            st.dataframe(
                low_drr_df,
                use_container_width=True,
                hide_index=True,
            
            )
            
            # Download button
            csv = low_drr_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Slow Moving Products (CSV)",
                data=csv,
                file_name=f"slow_moving_products_{pd.Timestamp.today().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.success("✅ No slow moving products identified")
    
    st.divider()
    
    # ---------------- Export All Analytics ----------------
    st.subheader("📤 Export Analytics Data")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        csv_category = df.groupby("minutes_category_new")["value"].sum().reset_index().to_csv(index=False)
        st.download_button(
            label="📥 Category Data",
            data=csv_category,
            file_name=f"category_value_{pd.Timestamp.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        csv_store = df.groupby("area_name_en")["value"].sum().reset_index().to_csv(index=False)
        st.download_button(
            label="📥 Store Data",
            data=csv_store,
            file_name=f"store_value_{pd.Timestamp.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        if "days_to_expiry" in df.columns:
            csv_expiry = df[["zsku", "product_title", "days_to_expiry", "qty", "value"]].to_csv(index=False)
            st.download_button(
                label="📥 Expiry Data",
                data=csv_expiry,
                file_name=f"expiry_data_{pd.Timestamp.today().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.button("📥 Expiry Data", disabled=True, use_container_width=True)
    
    with col4:
        csv_full = df.to_csv(index=False)
        st.download_button(
            label="📥 Full Dataset",
            data=csv_full,
            file_name=f"analytics_data_{pd.Timestamp.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
