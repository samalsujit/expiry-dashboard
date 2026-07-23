# Brand colors
COLORS = {
    "noon_yellow": "#FEDB00",
    "noon_yellow_dark": "#E8C800",
    "noon_yellow_light": "#FFF5CC",
    "noon_navy": "#1A2A4A",
    "noon_navy_light": "#2C3E6B",
    "noon_navy_dark": "#0F1A33",
    "white": "#FFFFFF",
    "gray_100": "#F8F9FA",
    "gray_200": "#E9ECEF",
    "gray_300": "#DEE2E6",
    "gray_400": "#CED4DA",
    "gray_500": "#ADB5BD",
    "gray_600": "#6C757D",
    "gray_700": "#495057",
    "gray_800": "#343A40",
    "gray_900": "#1A1A2E",
    "success": "#2CA02C",
    "danger": "#D62728",
    "warning": "#FFD93D",
    "info": "#17BECF",
}

# Chart colors
CHART_COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", 
    "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", 
    "#bcbd22", "#17becf"
]

def get_color(name):
    """Get a color by name"""
    return COLORS.get(name, "#000000")

def get_chart_colors(n=None):
    """Get chart colors"""
    if n:
        return CHART_COLORS[:n]
    return CHART_COLORS