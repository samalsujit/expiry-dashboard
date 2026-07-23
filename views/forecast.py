import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# Consistent color palette
COLOR_SCALE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]


def show_forecast():
    """Forecast page - Decision support for future expiry risks"""
    
    st.title("🔮 Expiry Forecast & Decision Support")
    
    if "dashboard_data" not in st.session_state:
        st.info("Please upload data first.")
        return
    
    dashboard = st.session_state.dashboard_data
    df = dashboard.get("df", pd.DataFrame())
    
    if df.empty:
        st.warning("No data available. Please check your filters.")
        return
    
    summary = dashboard["summary"]
    
    # ---------------- Risk Score Documentation ----------------
    with st.expander("ℹ️ How Risk Score is Calculated"):
        st.markdown("""
        **Risk Score Formula:** `Risk Score = Total Value / (Avg Days to Expiry + 1)`
        
        **Why this formula?**
        - **Total Value**: Higher value products represent greater financial risk
        - **Avg Days to Expiry**: Shorter timeframes require more urgent action
        - **+1**: Prevents division by zero and ensures products with 0 days are prioritized
        
        **Interpretation:**
        - **Higher Risk Score** = More urgent action required
        - Products with high value AND low days to expiry get the highest scores
        - This score helps prioritize which stores, categories, or products need attention first
        
        **Example:**
        - Store A: SAR 100,000 value, 5 avg days → Score = 100,000 / 6 = 16,667
        - Store B: SAR 50,000 value, 30 avg days → Score = 50,000 / 31 = 1,613
        - **Store A is more urgent** despite not having the highest value
        """)
    
    st.divider()
    
    # ---------------- Forecast Period Selector ----------------
    st.subheader("📅 Forecast Horizon")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        forecast_days = st.slider(
            "Select forecast horizon (days)",
            min_value=7,
            max_value=90,
            value=30,
            step=1,
            help="Number of days to forecast expiry risk"
        )
    
    with col2:
        view_by = st.selectbox(
            "Group by:",
            ["Category", "Store", "Product"],
            help="How to group the forecast data"
        )
    
    with col3:
        st.write("")
        st.write("")
        show_table = st.checkbox("Show Details", value=True)
    
    st.divider()
    
    # ---------------- Key Forecast Metrics ----------------
    st.subheader("📊 Forecast Summary")
    
    # Filter products expiring within forecast period
    forecast_df = df[(df["days_to_expiry"] >= 0) & (df["days_to_expiry"] <= forecast_days)].copy()
    
    # Calculate metrics
    total_products_at_risk = len(forecast_df)
    total_qty_at_risk = forecast_df["qty"].sum()
    total_value_at_risk = forecast_df["value"].sum()
    
    # Distribution by bucket
    def get_forecast_bucket(days):
        if days <= 3:
            return "0-3 Days"
        elif days <= 7:
            return "4-7 Days"
        elif days <= 14:
            return "8-14 Days"
        elif days <= 30:
            return "15-30 Days"
        else:
            return "31+ Days"
    
    forecast_df["forecast_bucket"] = forecast_df["days_to_expiry"].apply(get_forecast_bucket)
    bucket_summary = forecast_df.groupby("forecast_bucket").agg({
        "zsku": "count",
        "qty": "sum",
        "value": "sum"
    }).reset_index()
    bucket_summary.columns = ["Bucket", "Products", "Quantity", "Value"]
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Products at Risk",
        f"{total_products_at_risk:,}",
        delta=f"{total_products_at_risk/summary['total_products']*100:.1f}% of total" if summary['total_products'] > 0 else None
    )
    col2.metric(
        "Quantity at Risk",
        f"{total_qty_at_risk:,.0f}",
        delta=f"{total_qty_at_risk/summary['total_quantity']*100:.1f}% of total" if summary['total_quantity'] > 0 else None
    )
    col3.metric(
        "Value at Risk",
        f"SAR {total_value_at_risk:,.2f}",
        delta=f"{total_value_at_risk/summary['total_value']*100:.1f}% of total" if summary['total_value'] > 0 else None
    )
    col4.metric(
        "Avg Days to Expiry",
        f"{forecast_df['days_to_expiry'].mean():.1f}" if not forecast_df.empty else "N/A"
    )
    
    st.divider()
    
    # ---------------- Forecast Chart ----------------
    st.subheader("📈 Expiry Risk by Time Horizon")
    
    # Create cumulative forecast chart
    days_range = range(0, forecast_days + 1)
    cumulative_data = []
    
    for day in days_range:
        subset = df[(df["days_to_expiry"] >= 0) & (df["days_to_expiry"] <= day)]
        cumulative_data.append({
            "Day": day,
            "Products": len(subset),
            "Quantity": subset["qty"].sum(),
            "Value": subset["value"].sum()
        })
    
    cumulative_df = pd.DataFrame(cumulative_data)
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add traces
    fig.add_trace(
        go.Scatter(
            x=cumulative_df["Day"],
            y=cumulative_df["Products"],
            name="Products at Risk",
            line=dict(color="#1f77b4", width=3),
            mode="lines+markers"
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=cumulative_df["Day"],
            y=cumulative_df["Value"],
            name="Value at Risk (SAR)",
            line=dict(color="#d62728", width=3),
            mode="lines+markers"
        ),
        secondary_y=True
    )
    
    # Add threshold markers
    fig.add_vline(x=7, line_dash="dash", line_color="orange", annotation_text="7 Days")
    fig.add_vline(x=30, line_dash="dash", line_color="red", annotation_text="30 Days")
    
    fig.update_layout(
        title="Cumulative Products and Value at Risk",
        xaxis_title="Days from Today",
        font=dict(family="Arial, sans-serif"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_yaxes(title_text="Products at Risk", secondary_y=False)
    fig.update_yaxes(title_text="Value at Risk (SAR)", secondary_y=True)
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # ---------------- Grouped Forecast ----------------
    st.subheader(f"📊 Expiry Risk by {view_by}")
    
    if view_by == "Category":
        group_col = "minutes_category_new"
        group_label = "Category"
    elif view_by == "Store":
        group_col = "area_name_en"
        group_label = "Store"
    else:  # Product
        group_col = "zsku"
        group_label = "ZSKU"
    
    # Group forecast data
    grouped_forecast = forecast_df.groupby(group_col).agg({
        "qty": "sum",
        "value": "sum",
        "zsku": "count"
    }).reset_index()
    grouped_forecast.columns = [group_label, "Quantity", "Value", "Products"]
    grouped_forecast = grouped_forecast.sort_values("Value", ascending=False)
    
    if not grouped_forecast.empty:
        # Create two-column layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Top 10 bar chart
            top_10 = grouped_forecast.head(10)
            fig = px.bar(
                top_10,
                x=group_label,
                y="Value",
                title=f"Top 10 {view_by}s by Value at Risk",
                color="Value",
                color_continuous_scale="Reds",
                text="Value"
            )
            fig.update_traces(texttemplate='SAR %{text:,.0f}', textposition='outside')
            fig.update_layout(
                xaxis_title=view_by,
                yaxis_title="Value at Risk (SAR)",
                showlegend=False,
                font=dict(family="Arial, sans-serif"),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if show_table:
                st.dataframe(
                    grouped_forecast,
                    use_container_width=True,
                    hide_index=True,
                    height=400,
                )
            else:
                st.info("Toggle 'Show Details' to view the data table")
        
        # Additional insight: Show distribution of risk
        with st.expander("📊 Risk Distribution Insights"):
            # Show products by bucket
            bucket_dist = forecast_df.groupby("forecast_bucket").size().reset_index(name="Count")
            bucket_dist["Percentage"] = (bucket_dist["Count"] / bucket_dist["Count"].sum() * 100).round(1)
            
            fig = px.pie(
                bucket_dist,
                values="Count",
                names="forecast_bucket",
                title="Distribution of Products at Risk",
                color_discrete_sequence=COLOR_SCALE
            )
            fig.update_layout(
                font=dict(family="Arial, sans-serif"),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"No data available for {view_by}")
    
    st.divider()
    
    # ---------------- Action Required Products ----------------
    st.subheader("🚨 Products Requiring Immediate Action")
    
    # Products expiring in the next 7 days with significant quantity
    urgent_products = df[
        (df["days_to_expiry"] >= 0) & 
        (df["days_to_expiry"] <= 7) &
        (df["qty"] > 0)
    ].copy()
    
    if not urgent_products.empty:
        # Sort by value at risk
        urgent_products = urgent_products.sort_values("value", ascending=False)
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        col1.metric(
            "🚨 Products",
            f"{len(urgent_products):,}",
            delta="Requires immediate action"
        )
        col2.metric(
            "📦 Total Quantity",
            f"{urgent_products['qty'].sum():,.0f}"
        )
        col3.metric(
            "💰 Total Value at Risk",
            f"SAR {urgent_products['value'].sum():,.2f}",
            delta="Potential loss in 7 days"
        )
        
        # Show top 20 products
        st.subheader("🏷️ Top 20 Products at Risk")
        st.dataframe(
            urgent_products.head(20)[["zsku", "product_title", "days_to_expiry", "qty", "value", "area_name_en"]],
            use_container_width=True,
            hide_index=True,
        )
        
        # Download list
        csv_urgent = urgent_products.to_csv(index=False)
        st.download_button(
            label="📥 Download Action List (CSV)",
            data=csv_urgent,
            file_name=f"urgent_actions_{pd.Timestamp.today().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.success("✅ No products requiring immediate action in the next 7 days")
    
    st.divider()
    
    # ---------------- Store Risk Profile ----------------
    st.subheader("🏪 Store Risk Profile")
    
    store_risk = df.groupby("area_name_en").agg({
        "qty": "sum",
        "value": "sum",
        "days_to_expiry": "mean",
        "zsku": "count"
    }).reset_index()
    store_risk.columns = ["Store", "Total Quantity", "Total Value", "Avg Days to Expiry", "Products"]
    
    # Calculate Risk Score
    # Risk Score = Total Value / (Avg Days to Expiry + 1)
    store_risk["Risk Score"] = store_risk["Total Value"] / (store_risk["Avg Days to Expiry"] + 1)
    store_risk = store_risk.sort_values("Risk Score", ascending=False)
    
    if not store_risk.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(
                store_risk.head(15),
                x="Store",
                y="Risk Score",
                title="Store Risk Score (Higher = More Urgent)",
                color="Risk Score",
                color_continuous_scale="RdYlGn_r",
                hover_data=["Total Value", "Avg Days to Expiry"]
            )
            fig.update_layout(
                xaxis_title="Store",
                yaxis_title="Risk Score",
                showlegend=False,
                font=dict(family="Arial, sans-serif"),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.dataframe(
                store_risk.head(10),
                use_container_width=True,
                hide_index=True,
            )
        
        # Show all stores with risk score
        with st.expander("📋 All Stores with Risk Scores"):
            st.dataframe(
                store_risk,
                use_container_width=True,
                hide_index=True,
            )
        
        # FIXED: Calculate highest risk score outside the f-string
        highest_risk = f"{store_risk['Risk Score'].max():.0f}" if not store_risk.empty else "N/A"
        top_risk_store = store_risk.iloc[0]['Store'] if not store_risk.empty else "N/A"
    else:
        highest_risk = "N/A"
        top_risk_store = "N/A"
    
    st.divider()
    
    # ---------------- Financial Impact ----------------
    st.subheader("💰 Financial Impact Analysis")
    
    if not forecast_df.empty:
        # Calculate impact by bucket
        impact_summary = forecast_df.groupby("forecast_bucket").agg({
            "value": "sum",
            "qty": "sum"
        }).reset_index()
        impact_summary["% of Total Value"] = (impact_summary["value"] / impact_summary["value"].sum() * 100).round(1)
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            fig = px.bar(
                impact_summary,
                x="forecast_bucket",
                y="value",
                title="Potential Financial Impact by Time Horizon",
                color="value",
                color_continuous_scale="Reds",
                text="value"
            )
            fig.update_traces(texttemplate='SAR %{text:,.0f}', textposition='outside')
            fig.update_layout(
                xaxis_title="Time Horizon",
                yaxis_title="Value at Risk (SAR)",
                showlegend=False,
                font=dict(family="Arial, sans-serif"),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.dataframe(
                impact_summary,
                use_container_width=True,
                hide_index=True,
            )
        
        # Total estimated impact - FIXED: Use variables calculated above
        st.info(f"""
        **💡 Key Insight:** 
        - Total estimated value at risk within {forecast_days} days: **SAR {total_value_at_risk:,.2f}**
        - {len(urgent_products)} products require action within 7 days
        - **SAR {urgent_products['value'].sum():,.2f}** could be lost if no action is taken in the next 7 days
        - **Priority:** Focus on **{top_risk_store}** with risk score **{highest_risk}**
        """)
    else:
        st.info("No forecast data available for financial impact analysis")
