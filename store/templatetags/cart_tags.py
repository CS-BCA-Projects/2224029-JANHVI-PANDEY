from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def to_inr(value):
    try:
        return f"₹{float(value):.2f}"
    except (ValueError, TypeError):
        return "₹0.00"