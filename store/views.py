from django.shortcuts import render
from .models import Product
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItem
from .models import Order, OrderItem

def home(request):
    # Abhi ke liye simple welcome page
    return render(request, 'store/index.html', {'message': 'Welcome to SnapShop Store!'})

def home(request):
    products = Product.objects.all()  # Sab products fetch karo
    return render(request, 'store/index.html', {'products': products})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.cartitem_set.all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def update_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('view_cart')

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.delete()
    return redirect('view_cart')

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.cartitem_set.all()
    if not cart_items:
        return redirect('view_cart')

    total_price = sum(item.product.price * item.quantity for item in cart_items)
    order = Order.objects.create(user=request.user, total_price=total_price)

    for item in cart_items:
        OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
        item.product.stock -= item.quantity
        item.product.save()

    cart_items.delete()  # Cart khali karo
    return render(request, 'store/order_confirmation.html', {'order': order})

def search_products(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query) | products.filter(description__icontains=query)
    if category:
        products = products.filter(category=category)

    return render(request, 'store/index.html', {'products': products, 'query': query})

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/profile.html', {'orders': orders})