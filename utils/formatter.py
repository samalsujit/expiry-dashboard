def format_currency(value, currency="SAR"):
    """Format currency values"""
    if value is None or (isinstance(value, float) and value != value):
        return "N/A"
    return f"{currency} {value:,.2f}"


def format_quantity(value):
    """Format quantity values"""
    if value is None or (isinstance(value, float) and value != value):
        return "N/A"
    return f"{value:,.0f}"


def format_percent(value, decimals=1):
    """Format percentage values"""
    if value is None or (isinstance(value, float) and value != value):
        return "N/A"
    return f"{value:.{decimals}f}%"


def format_days(value):
    """Format days values"""
    if value is None or (isinstance(value, float) and value != value):
        return "N/A"
    if value == 0:
        return "Today"
    elif value < 0:
        return f"{abs(value):.0f} days ago"
    else:
        return f"{value:.0f} days"


def format_date(value, fmt="%d %b %Y"):
    """Format date values"""
    if value is None:
        return "N/A"
    try:
        if hasattr(value, 'strftime'):
            return value.strftime(fmt)
        return str(value)
    except:
        return str(value)


def format_number(value):
    """Format numbers with commas"""
    if value is None or (isinstance(value, float) and value != value):
        return "N/A"
    return f"{value:,.0f}"


def format_boolean(value):
    """Format boolean values"""
    if value is None:
        return "N/A"
    return "✅ Yes" if value else "❌ No"


def truncate_text(text, max_length=50):
    """Truncate text to max_length"""
    if not text:
        return ""
    text = str(text)
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."