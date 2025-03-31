from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.contrib.auth import authenticate, login, logout
from .models import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages


def home(request):
    homepage = HomePage.objects.first()
    context = {
        'bestsellers': homepage.bestsellers.all()[:3] if homepage else [],
        'new_product': homepage.new_products.first() if homepage else None,
        'background_image': homepage.background_image if homepage else None,
        'homepage': homepage
    }
    return render(request, 'store/home.html', context)

def menu(request):
    category = request.GET.get('category')
    search = request.GET.get('search')
    products = Product.objects.all()
    
    if category:
        products = products.filter(category=category)
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(category__icontains=search) |
            Q(ingredients__icontains=search)
        )
    
    context = {
        'products': products,
        'categories': Product.CATEGORIES,
    }
    return render(request, 'store/menu.html', context)

def about(request):
    return render(request, 'store/about.html')

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Tính số lượng sản phẩm chưa thanh toán
    reserved_quantity = CartItem.objects.filter(product=product, cart__user=request.user).aggregate(Sum('quantity'))['quantity__sum'] or 0
    available_quantity = max(product.stock - reserved_quantity, 0)

    return render(request, 'store/product_detail.html', {
        'product': product,
        'available_quantity': available_quantity,
    })


# def product_detail(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     return render(request, 'store/product_detail.html', {'product': product})

# @login_required
# def profile(request):
#     customer = get_object_or_404(Customer, user=request.user)
#     return render(request, 'store/profile.html', {'customer': customer})

@login_required
def profile(request):
    customer, created = Customer.objects.get_or_create(user=request.user)
    return render(request, 'store/profile.html', {'customer': customer})

@login_required
def edit_profile(request):
    customer = get_object_or_404(Customer, user=request.user)

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')

        if phone_number is not None:
            customer.phone_number = phone_number
        if address is not None:
            customer.address = address

        customer.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('store:profile')  # Chuyển hướng về trang hồ sơ sau khi cập nhật

    return render(request, 'store/edit_profile.html', {'customer': customer})


# @login_required
# def cart(request):
#     # Implement cart logic using sessions or database
#     return render(request, 'store/cart.html')

# @login_required
# def cart(request):
#     cart, created = Cart.objects.get_or_create(user=request.user)
#     cart_items = CartItem.objects.filter(cart=cart)
#     total_price = sum(item.product.price * item.quantity for item in cart_items)

#     context = {
#         'cart_items': cart_items,
#         'total_price': total_price,
#     }
#     return render(request, 'store/cart.html', context)

@login_required
def cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    
    # Tính tổng tiền từng sản phẩm và tổng tiền của giỏ hàng
    for item in cart_items:
        item.total_price = item.product.price * item.quantity  # Tạo thuộc tính tạm thời để hiển thị

    subtotal = sum(item.total_price for item in cart_items)
    shipping_fee = 0 if subtotal >= 50 else 10  # Miễn phí ship nếu >= 50$
    total_price = subtotal + shipping_fee

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': total_price,
    }
    return render(request, 'store/cart.html', context)


# @login_required
# def add_to_cart(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#      # Kiểm tra nếu sản phẩm còn hàng
#     if product.stock > 0:
#         # Lấy hoặc tạo giỏ hàng cho user (tùy vào cách bạn triển khai)
#         cart, created = Cart.objects.get_or_create(user=request.user)  

#         # Kiểm tra xem sản phẩm đã có trong giỏ chưa
#         cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

#         # Tăng số lượng sản phẩm trong giỏ hàng
#         cart_item.quantity += 1  
#         cart_item.save()

#         # Giảm số lượng hàng tồn kho
#         product.stock -= 1  
#         product.save()
#     # Xử lý logic thêm sản phẩm vào giỏ hàng
#     return redirect('store:product_detail', product_id=product.id)  # Chỉnh sửa tùy theo trang bạn muốn quay lại

# @login_required
# def add_to_cart(request, product_id):
#     product = get_object_or_404(Product, id=product_id)

#     if product.stock > 0:
#         # Đảm bảo mỗi user có một giỏ hàng
#         cart, created = Cart.objects.get_or_create(user=request.user)

#         # Thêm sản phẩm vào giỏ hàng
#         cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
#          # Nếu sản phẩm chưa có trong giỏ hàng, gán số lượng từ form; nếu có rồi, chỉ tăng số lượng khi người dùng muốn thêm nhiều hơn
#         quantity = int(request.POST.get("quantity", 1))
        
#         if created:
#             cart_item.quantity = quantity  # Gán số lượng từ người dùng chọn
#         else:
#             cart_item.quantity += quantity  # Tăng số lượng khi thêm tiếp
#         cart_item.save()

#     return redirect('store:cart')  # Chuyển hướng về trang giỏ hàng

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    try:
        quantity = int(request.POST.get("quantity", 1))
        if quantity <= 0:
            raise ValueError
    except ValueError:
        messages.error(request, "Invalid quantity selected.")
        return redirect('store:product_detail', product_id=product.id)

    # Kiểm tra nếu sản phẩm đã tồn tại trong giỏ
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if created:
        cart_item.quantity = quantity  # Nếu là sản phẩm mới, đặt đúng số lượng
    else:
        cart_item.quantity = quantity  # Đặt lại số lượng chứ không cộng dồn

    cart_item.save()
    messages.success(request, f"{product.name} has been added to your cart with quantity {quantity}.")
    return redirect('store:cart')


# @login_required
# def cart_detail(request):
#     cart_items = Cart.objects.all()
#     total_price = sum(item.product.price * item.quantity for item in cart_items)
    
#     context = {
#         'cart_items': cart_items,
#         'total_price': total_price,
#     }
#     return render(request, 'store/cart.html', context)
@login_required
def cart_detail(request):
    cart = Cart.objects.filter(user=request.user).first()
    cart_items = CartItem.objects.filter(cart=cart) if cart else []
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'store/cart.html', context)

@login_required
def remove_from_cart(request, product_id):
    cart = Cart.objects.get(user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
    cart_item.delete()
    return redirect('store:cart')

# @login_required
# def update_cart(request, product_id):
#     if request.method == 'POST':
#         cart = Cart.objects.get(user=request.user)
#         cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
#         quantity = int(request.POST.get('quantity', 1))
#         cart_item.quantity = max(1, quantity)  # Đảm bảo số lượng >= 1
#         cart_item.save()
#     return redirect('store:cart')

@login_required
def update_cart(request, product_id):
    cart = Cart.objects.get(user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)

    if request.method == 'POST':
        quantity_str = request.POST.get('quantity', '').strip()

        # Kiểm tra nếu giá trị rỗng hoặc không phải số hợp lệ
        if not quantity_str.isdigit():
            messages.error(request, "Invalid quantity. Please enter a valid number.")
            return redirect('store:cart')

        quantity = int(quantity_str)

        # Kiểm tra số lượng nằm trong giới hạn hợp lệ
        reserved_quantity = CartItem.objects.filter(product=cart_item.product).exclude(id=cart_item.id).aggregate(Sum('quantity'))['quantity__sum'] or 0
        available_quantity = max(cart_item.product.stock - reserved_quantity, 0)

        if quantity < 1:
            messages.error(request, "Quantity must be at least 1.")
            quantity = 1
        elif quantity > available_quantity:
            messages.error(request, f"Only {available_quantity} items available.")
            quantity = available_quantity

        cart_item.quantity = quantity
        cart_item.save()

    return redirect('store:cart')


# @login_required
# def payment(request):
#     customer = get_object_or_404(Customer, user=request.user)
#     payment_methods = Payment.objects.all()
    
#     if request.method == 'POST':
#         # Add payment processing logic here
#         pass
    
#     context = {
#         'customer': customer,
#         'payment_methods': payment_methods,
#     }
#     return render(request, 'store/payment.html', context)

@login_required
def payment(request):
    customer = get_object_or_404(Customer, user=request.user)
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    payment_methods = Payment.objects.all()

    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect('store:cart')

    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    shipping_fee = 0 if subtotal >= 50 else 10
    total = subtotal + shipping_fee

    if request.method == 'POST':
        payment_method_id = request.POST.get('payment_method')
        payment_method = get_object_or_404(Payment, id=payment_method_id)
        
        # Tạo đơn hàng mới
        order = Order.objects.create(
            customer=customer,
            status='unpaid',
            # status='unpaid' if payment_method.name != "COD" else 'paid',
            payment_method=payment_method,
            total_amount=total
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            # item.product.stock -= item.quantity
            # item.product.save()

        cart_items.delete()  # Xóa giỏ hàng sau khi đặt hàng
        
        if payment_method.name == "COD":
            messages.success(request, "Your order has been placed successfully!")
        else:
            messages.info(request, "Your order is pending confirmation. Please wait for admin approval.")

        return redirect('store:home')

    return render(request, 'store/payment.html', {
        'customer': customer,
        'cart_items': cart_items,
        'payment_methods': payment_methods,
        'subtotal': subtotal,
        'total': total,
    })


@login_required
def confirm_payment(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect('store:cart')

    # Trừ stock sau khi thanh toán thành công
    for item in cart_items:
        product = item.product
        if product.stock >= item.quantity:
            product.stock -= item.quantity
            product.save()
        else:
            messages.error(request, f"Not enough stock for {product.name}.")
            return redirect('store:cart')

    # Xóa giỏ hàng sau khi đặt hàng thành công
    cart_items.delete()
    
    messages.success(request, "Order placed successfully!")
    return redirect('store:home')


def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('store:home')

def login_view(request):
    username = ''  # Biến này dùng để giữ lại username khi nhập sai
    if request.method == "POST":
        username = request.POST.get("username",'').strip()
        password = request.POST.get("password",'').strip()
        
        if not username or not password:
            messages.error(request, "Username and password are required")
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!") 
                return redirect('store:home')  # Change 'home' to your main page
            else:
                messages.error(request, "Invalid username or password")
    return render(request, 'store/login.html', {"username": username})

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username",'').strip()
        email = request.POST.get("email", "").strip()
        phone_number = request.POST.get("phone_number",'').strip()
        address = request.POST.get("address",'').strip()
        password1 = request.POST.get("password1",'').strip()
        password2 = request.POST.get("password2",'').strip()

        if not username or not phone_number or not address or not password1 or not password2:
            messages.error(request, "All fields except email are required")
        elif password1 != password2:
            messages.error(request, "Passwords do not match")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            # Automatically create a Customer profile
            Customer.objects.create(user=user, phone_number=phone_number, address=address)
            
            login(request, user)
            return redirect('store:home')

    return render(request, 'store/register.html')


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'store/profile.html', {'profile': profile})