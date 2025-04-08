from django.urls import path
from .views import home, add_to_cart, view_cart, update_cart, remove_from_cart, checkout, profile, buy_now

app_name = 'store'  

urlpatterns = [
    path('', home, name='home'),
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('update/<int:item_id>/', update_cart, name='update_cart'),
    path('remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('checkout/', checkout, name='checkout'),
    path('profile/', profile, name='profile'),
    path('buy-now/<int:product_id>/', buy_now, name='buy_now'),
]