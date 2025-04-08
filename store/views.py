from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Cart, CartItem, Order, OrderItem, Address
from django.urls import reverse  # Import reverse for URL resolution

def home(request):
    section = request.GET.get('section', '')  # Get section from query parameter
    query = request.GET.get('q', '')  # For search functionality
    category = request.GET.get('category', '')

    products = Product.objects.all()

    # Filter by section if provided
    if section:
        products = products.filter(section=section)

    # Filter by category if provided
    if category:
        products = products.filter(category=category)

    # Filter by search query if provided
    if query:
        products = products.filter(name__icontains=query) | products.filter(description__icontains=query)

    return render(request, 'store/index.html', {
        'products': products,
        'query': query,
        'selected_section': section,
        'selected_category': category,
        'message': 'Welcome to SnapShop Store!'
    })

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if product.stock < 1:
        messages.error(request, f"{product.name} is out of stock!")
        return redirect(reverse('store:home'))

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created and cart_item.quantity + 1 > product.stock:
        messages.error(request, f"Only {product.stock} units of {product.name} are available!")
        return redirect(reverse('store:view_cart'))
    
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    messages.success(request, f"{product.name} added to cart!")
    return redirect(reverse('store:view_cart'))

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cart_items.all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        if item_id:
            return redirect(reverse('store:update_cart', kwargs={'item_id': int(item_id)}))
    
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def update_cart(request, item_id):
    cart = Cart.objects.get(user=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > cart_item.product.stock:
            messages.error(request, f"Only {cart_item.product.stock} units of {cart_item.product.name} are available!")
            return redirect(reverse('store:view_cart'))
            
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, "Cart updated successfully!")
        else:
            cart_item.delete()
            messages.success(request, "Item removed from cart!")
        return redirect(reverse('store:view_cart'))
    
    cart_items = cart.cart_items.all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def remove_from_cart(request, item_id):
    cart = Cart.objects.get(user=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()
    messages.success(request, "Item removed from cart!")
    return redirect(reverse('store:view_cart'))

@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cart_items.all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if not cart_items:
        messages.error(request, "Your cart is empty! Add some products to proceed.")
        return redirect(reverse('store:view_cart'))  # Ensure redirect on empty cart

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2', '')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country', 'India')

        if not all([full_name, phone_number, address_line_1, city, state, postal_code]):
            messages.error(request, "Please fill in all required address fields!")
            return render(request, 'store/checkout.html', {'cart_items': cart_items, 'total_price': total_price})

        address = Address.objects.create(
            user=request.user,
            full_name=full_name,
            phone_number=phone_number,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country
        )

        order = Order.objects.create(
            user=request.user,
            address=address,
            total_price=total_price,
            payment_method="Cash on Delivery"
        )
        
        for item in cart_items:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
            item.product.stock -= item.quantity
            if item.product.stock < 0:
                messages.error(request, f"Not enough stock for {item.product.name}!")
                return redirect(reverse('store:view_cart'))
            item.product.save()

        cart_items.delete()
        messages.success(request, "Order placed successfully! Payment will be Cash on Delivery.")
        return redirect(reverse('store:profile'))
    else:  # Ensure GET request returns a response
        return render(request, 'store/checkout.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/profile.html', {'orders': orders})

@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if product.stock < 1:
        messages.error(request, f"{product.name} is out of stock!")
        return redirect(reverse('store:home'))

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2', '')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country', 'India')

        if not all([full_name, phone_number, address_line_1, city, state, postal_code]):
            messages.error(request, "Please fill in all required address fields!")
            return render(request, 'store/buy_now.html', {'product': product})

        address = Address.objects.create(
            user=request.user,
            full_name=full_name,
            phone_number=phone_number,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country
        )

        order = Order.objects.create(
            user=request.user,
            address=address,
            total_price=product.price,
            payment_method="Cash on Delivery"
        )
        OrderItem.objects.create(order=order, product=product, quantity=1)
        
        product.stock -= 1
        if product.stock < 0:
            messages.error(request, f"Not enough stock for {product.name}!")
            return redirect(reverse('store:home'))
        product.save()

        messages.success(request, "Order placed successfully! Payment will be Cash on Delivery.")
        return redirect(reverse('store:home'))
    else:
        return render(request, 'store/buy_now.html', {'product': product})