from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .models import Product, Category
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.shortcuts import redirect

from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from rest_framework import viewsets
from .serializer import *
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes



def login_view(request): 
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')
            else:
                products = Product.objects.all()  # Use 'Product', not 'product'
                return render(request, "home.html", {"products": products})
        else:
            return HttpResponse("Invalid credentials")
    return render(request, "login.html")

'''def signup(request):
  if request.method=='POST':
    cname=request.POST.get('fullname')
    email=request.POST.get('email')
    phone=request.POST.get('mobile')
    password=request.POST.get('password')
    psw=request.POST.get('confirm-password')
    User_details.objects.create(name=cname, Email_id=email, Phone_number=phone,password=password,confpassword=psw)
    return HttpResponse("User registered successfully")

  return render(request,"signup.html")'''



def signup(request):
    if request.method=='POST':
      fname=request.POST.get('firstname')
      lname=request.POST.get('lastname')
      email=request.POST.get('email')
      username=request.POST.get('username')
      password=request.POST.get('password')
      User.objects.create_user(first_name=fname,last_name=lname,email=email,username=username,password=password)
      return HttpResponse("User registered successfully")
  
    return render(request,"signup.html")

def productadd(request):
   c=Category.objects.all()
   if request.method=='POST':
     pname=request.POST.get('name')
     price=request.POST.get('price')
     stock=request.POST.get('stock')
     cat=request.POST.get('categ')
     description=request.POST.get('description')
     catobj=Category.objects.get(id=cat)
     productimage=request.FILES.get('image')
     fs=FileSystemStorage()
     filename=fs.save(productimage.name,productimage)
     Product.objects.create(name=pname,price=price,stock=stock,categ=catobj,product_image=filename, description=description )
     return HttpResponse("Product added Successfully")
   return render(request,"productadd.html",{"categories": c})

def logout_user(request):
    logout(request)
    return redirect('login')

def home(request):
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    pname = request.GET.get('name', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    products = Product.objects.all()
    if selected_category:
        products = products.filter(categ__id=selected_category)
    if pname:
        products = products.filter(name__icontains=pname)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    return render(request, "home.html", {
        "products": products,
        "categories": categories,
        "selected_category": selected_category,
    })

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
    else:
        cart = request.session.get('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
        request.session['cart'] = cart
    return redirect('cart')

def cart_view(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        cart_products = [{'product': item.product, 'quantity': item.quantity} for item in cart_items]
        total = sum(item.product.price * item.quantity for item in cart_items)
    else:
        cart = request.session.get('cart', {})
        cart_products = []
        total = 0
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            cart_products.append({'product': product, 'quantity': quantity})
            total += product.price * quantity
    return render(request, 'cart.html', {'cart_products': cart_products, 'total': total})

def admin_dashboard(request):
    order_count = Order.objects.count()
    product_count = Product.objects.count()
    user_count = User.objects.count()
    products = Product.objects.all()
    users = User.objects.all()
    return render(request, 'admin.html', {
        'order_count': order_count,
        'product_count': product_count,
        'user_count': user_count,
        'products': products,
        'users': users,
    })

def admin_orders(request):
    orders = Order.objects.select_related('user', 'product').all().order_by('-order_date')
    return render(request, 'admin_orders.html', {'orders': orders})

def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        product.category = request.POST.get('category')
        # Handle image update if needed
        product.save()
        return redirect('admin_dashboard')
    return render(request, 'edit_product.html', {'product': product})

def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('admin_dashboard')

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})

def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = 1
    user = request.user if request.user.is_authenticated else None

    if request.user.is_authenticated:
        cart_item = CartItem.objects.filter(user=request.user, product=product).first()
        if cart_item:
            quantity = cart_item.quantity
            cart_item.delete()
    else:
        cart = request.session.get('cart', {})
        quantity = cart.get(str(product_id), 1)
        cart.pop(str(product_id), None)
        request.session['cart'] = cart

    # Decrease stock
    if product.stock >= quantity:
        product.stock -= quantity
        product.save()
        # Create an order record (no status)
        Order.objects.create(
            user=request.user,
            product=product,
            quantity=quantity
        )
    else:
        return render(request, 'order-confirmation.html', {'error': 'Not enough stock!'})

    cart_products = [{
        'product': product,
        'quantity': quantity,
        'subtotal': product.price * quantity,
    }]
    total = product.price * quantity

    return render(request, 'order-confirmation.html', {
        'cart_products': cart_products,
        'total': total,
        'user': request.user,
    })

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
    return redirect('cart')

def update_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if request.user.is_authenticated:
            cart_item = CartItem.objects.filter(user=request.user, product_id=product_id).first()
            if cart_item:
                if quantity > 0:
                    cart_item.quantity = quantity
                    cart_item.save()
                else:
                    cart_item.delete()
        else:
            cart = request.session.get('cart', {})
            if quantity > 0:
                cart[str(product_id)] = quantity
            else:
                cart.pop(str(product_id), None)
            request.session['cart'] = cart
    return redirect('cart')

def order_confirmation(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
            cart_products = []
            total = 0
            for item in cart_items:
                # Decrease stock
                if item.product.stock >= item.quantity:
                    item.product.stock -= item.quantity
                    item.product.save()
                # Create an Order object
                Order.objects.create(
                    user=request.user,
                    product=item.product,
                    quantity=item.quantity
                )
                # Prepare order summary
                subtotal = item.product.price * item.quantity
                cart_products.append({'product': item.product, 'quantity': item.quantity, 'subtotal': subtotal})
                total += subtotal
            cart_items.delete()  # Clear cart
        else:
            cart = request.session.get('cart', {})
            cart_products = []
            total = 0
            for product_id, quantity in cart.items():
                product = Product.objects.get(id=product_id)
                # Decrease stock
                if product.stock >= quantity:
                    product.stock -= quantity
                    product.save()
                # Create an Order object (user=None for guest)
                Order.objects.create(
                    user=None,
                    product=product,
                    quantity=quantity
                )
                subtotal = product.price * quantity
                cart_products.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
                total += subtotal
            request.session['cart'] = {}  # Clear cart
        return render(request, 'order-confirmation.html', {
            'cart_products': cart_products,
            'total': total,
            'user': request.user,
        })
    else:
        return redirect('cart')

def product_filter(request):
    pname = request.GET.get('name', '')
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    products = Product.objects.all()
    if pname:
        products = products.filter(name__icontains=pname)
    if selected_category:
        products = products.filter(categ__id=selected_category)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    return render(request, 'home.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
    })

def admin_products(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    pname = request.GET.get('name', '')
    selected_category = request.GET.get('category')
    if pname:
        products = products.filter(name__icontains=pname)
    if selected_category:
        products = products.filter(categ__id=selected_category)
    return render(request, 'admin_products.html', {
        'products': products,
        'categories': categories,
    })

def admin_customers(request):
    users = User.objects.all()
    return render(request, 'admin_customers.html', {'users': users})


#api views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_details(request):
    user_data= User.objects.all()
    serializer = UserSerializer(user_data, many=True)
    return Response(serializer.data)

@api_view(['GET','POST'])
def post_user_details(request):
    if request.method == 'POST':
      fname = request.data.get('firstname')
      lname = request.data.get('lastname')
      email = request.data.get('email')
      username = request.data.get('username')
      password = request.data.get('password')
      User.objects.create_user(first_name=fname,last_name=lname,email=email,username=username,password=password)
      return Response("User registered successfully")
  
    return Response("Please respond to the form")

@api_view(['PUT','GET'])
def update_user_details(request, user_id):
    user =User.objects.filter(id=user_id)
    if request.method=='PUT':
        fname = request.data.get('firstname')
        lname = request.data.get('lastname')
        email = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')
        user.update(first_name=fname, last_name=lname, email=email, username=username, password=password)
        return Response("User details updated successfully")
    
    return Response("Please provide valid data")

@api_view(['DELETE'])
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return Response({"message": "User deleted successfully"}, status=200)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

@require_POST
@login_required
@user_passes_test(lambda u: u.is_staff)
def approve_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'approved'
    order.save()
    return JsonResponse({'status': 'approved'})

@require_POST
@login_required
@user_passes_test(lambda u: u.is_staff)
def reject_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'rejected'
    order.save()
    return JsonResponse({'status': 'rejected'})

@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'user_orders.html', {'orders': orders})


