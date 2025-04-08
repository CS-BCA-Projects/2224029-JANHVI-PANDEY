from django import template

register = template.Library()

@register.filter
def to_inr(value):
    try:
        # Convert value to float and format it as INR
        value = float(value)
        return f"₹{value:,.2f}"  # Example: ₹1,234.56
    except (ValueError, TypeError):
        return value  # Return original value if conversion fails