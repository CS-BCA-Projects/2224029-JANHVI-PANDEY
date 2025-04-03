from django import template

register = template.Library()

@register.filter
def to_inr(value):
    try:
        # Just format the value with ₹ symbol and thousands separator
        inr_value = float(value)
        return f"₹{inr_value:,.2f}"  # e.g., ₹5,83,250.00
    except (ValueError, TypeError) as e:
        print(f"Error formatting to INR: {value}, Error: {e}")
        return "₹0.00"  # Fallback value