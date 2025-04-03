from django.contrib import admin
from .models import Product, Cart, CartItem, Order, OrderItem

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_inr', 'stock', 'section')
    list_filter = ('section',)
    search_fields = ('name', 'description')

    def price_inr(self, obj):
        return f"₹{obj.price:,.2f}"  # Display price with ₹ in admin list view
    price_inr.short_description = "Price (INR)"  # Column header in admin

    # Custom form to add help text
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'price', 'stock', 'image', 'section')
        }),
    )
    formfield_overrides = {
        'price': {'help_text': 'Enter the price in Indian Rupees (₹).'},
    }

admin.site.register(Product, ProductAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)