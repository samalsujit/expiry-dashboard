import streamlit as st


def render_kpi_card(label, value, icon=None, change=None, change_type=None):
    """Render a single KPI card"""
    
    change_html = ""
    if change:
        change_class = "positive" if change_type == "positive" else "negative" if change_type == "negative" else "neutral"
        change_html = f'<div class="kpi-change {change_class}">{change}</div>'
    
    icon_html = f'<div class="kpi-icon">{icon}</div>' if icon else ""
    
    st.markdown(f"""
    <div class="kpi-card">
        {icon_html}
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
        {change_html}
    </div>
    """, unsafe_allow_html=True)


def render_kpi_row(metrics):
    """Render a row of KPI cards
    
    Args:
        metrics: List of dicts with keys: label, value, icon, change, change_type
    """
    cols = st.columns(len(metrics))
    for idx, metric in enumerate(metrics):
        with cols[idx]:
            render_kpi_card(
                label=metric.get("label", ""),
                value=metric.get("value", ""),
                icon=metric.get("icon"),
                change=metric.get("change"),
                change_type=metric.get("change_type")
            )


def render_kpi_grid(metrics, cols=4):
    """Render KPI cards in a grid
    
    Args:
        metrics: List of dicts with keys: label, value, icon, change, change_type
        cols: Number of columns
    """
    rows = [metrics[i:i+cols] for i in range(0, len(metrics), cols)]
    
    for row in rows:
        render_kpi_row(row)