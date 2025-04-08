from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from store.models import Product, Order, OrderItem
from .forms import ProductForm

@login_required
def seller_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    products = Product.objects.filter(user=request.user)
    seller_orders = Order.objects.filter(orderitem__product__user=request.user).distinct().order_by('-created_at')
    print("Looking for template at:", "dashboard.html")
    return render(request, 'dashboard.html', {'products': products, 'orders': seller_orders})

@login_required
def add_product(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user  # Link product to seller
            product.save()
            messages.success(request, "Product added successfully!")
            return redirect('seller_dashboard')
    else:
        form = ProductForm()
    return render(request, 'seller_dashboard/add_product.html', {'form': form})

@login_required
def edit_product(request, product_id):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id, user=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('seller_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'seller_dashboard/edit_product.html', {'form': form})

@login_required
def delete_product(request, product_id):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id, user=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect('seller_dashboard')
    return render(request, 'seller_dashboard/delete_product.html', {'product': product})