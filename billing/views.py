from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from .models import MenuItem, Category, Order, CarouselImage, UserProfile
from .forms import SignUpForm, UserProfileForm, UserUpdateForm
import json
from decimal import Decimal

def home(request):
    categories = Category.objects.filter(is_active=True)
    menu_items = MenuItem.objects.filter(is_available=True)
    carousel_images = CarouselImage.objects.filter(is_active=True)
    
    # Get user profile details if logged in
    user_data = {}
    if request.user.is_authenticated:
        user_data = {
            'name': request.user.get_full_name() or request.user.username,
            'phone': request.user.profile.phone if hasattr(request.user, 'profile') else '',
            'address': request.user.profile.address if hasattr(request.user, 'profile') else '',
            'email': request.user.email,
        }
    
    context = {
        'restaurant_name': settings.RESTAURANT_NAME,
        'categories': categories,
        'menu_items': menu_items,
        'carousel_images': carousel_images,
        'delivery_charge': settings.DELIVERY_CHARGE,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'vat_percentage': settings.VAT_PERCENTAGE,
        'user_authenticated': request.user.is_authenticated,
    }
    return render(request, 'billing/home.html', context)

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.profile.phone = form.cleaned_data.get('phone')
            user.profile.address = form.cleaned_data.get('address')
            user.profile.save()
            login(request, user)
            messages.success(request, f'Welcome to {settings.RESTAURANT_NAME}, {user.username}!')
            return redirect('home')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = SignUpForm()
    
    return render(request, 'billing/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password!')
    
    return render(request, 'billing/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('home')

@login_required
def profile_view(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'billing/profile.html', context)

@login_required
def my_orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'billing/my_orders.html', {'orders': orders})

@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = json.loads(order.items_json)
    return render(request, 'billing/order_detail.html', {'order': order, 'items': items})

@csrf_exempt
def calculate_bill(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            subtotal = Decimal('0')
            
            for item in items:
                subtotal += Decimal(str(item['price'])) * int(item['quantity'])
            
            delivery_charge = Decimal('0')
            if subtotal < settings.FREE_DELIVERY_THRESHOLD:
                delivery_charge = Decimal(str(settings.DELIVERY_CHARGE))
            
            vat_amount = subtotal * Decimal(str(settings.VAT_PERCENTAGE)) / Decimal('100')
            total = subtotal + delivery_charge + vat_amount
            
            return JsonResponse({
                'subtotal': float(subtotal),
                'delivery_charge': float(delivery_charge),
                'vat_amount': float(vat_amount),
                'vat_percentage': settings.VAT_PERCENTAGE,
                'total': float(total),
                'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def place_order(request):
    """Simple order placement without complex payment gateway"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            customer_name = data.get('customer_name', '').strip()
            customer_phone = data.get('customer_phone', '').strip()
            customer_address = data.get('customer_address', '').strip()
            payment_method = data.get('payment_method', 'cod')
            
            if not customer_name or not customer_phone:
                return JsonResponse({'error': 'Name and phone are required'}, status=400)
            
            if not items:
                return JsonResponse({'error': 'Cart is empty'}, status=400)
            
            subtotal = Decimal('0')
            for item in items:
                subtotal += Decimal(str(item['price'])) * int(item['quantity'])
            
            delivery_charge = Decimal('0')
            if subtotal < settings.FREE_DELIVERY_THRESHOLD:
                delivery_charge = Decimal(str(settings.DELIVERY_CHARGE))
            
            vat_amount = subtotal * Decimal(str(settings.VAT_PERCENTAGE)) / Decimal('100')
            total = subtotal + delivery_charge + vat_amount
            
            # Create order
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                customer_name=customer_name,
                customer_phone=customer_phone,
                customer_address=customer_address,
                items_json=json.dumps(items),
                subtotal=subtotal,
                delivery_charge=delivery_charge,
                vat_amount=vat_amount,
                total=total,
                payment_method=payment_method,
                payment_status='PENDING' if payment_method == 'cod' else 'PAID',
                status='CONFIRMED'
            )
            
            return JsonResponse({
                'success': True,
                'order_id': order.id,
                'total': float(total),
                'payment_method': payment_method
            })
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)