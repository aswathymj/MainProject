from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser
from django.contrib.auth.decorators import login_required
from .models import Category,SubCategory,Product,Cart,Payment,PhoneCategory,PhoneSubCategory,PhoneModel,Complaint,ServiceRequest,TermsAndConditions, Payments, Wishlist,Feedback,OldPhoneCategory, OldPhoneSubCategory,OldPhoneModel,PhoneRepairRequest
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import paypalrestsdk
from django.conf import settings
import razorpay
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
import json
from .forms import ComplaintForm
import joblib
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from datetime import datetime
from django.contrib.auth import update_session_auth_hash

# Create your views here.
def index(request):
    return render(request, 'index.html')

def admin_view(request):
    category_count = Category.objects.count()
    product_count = Product.objects.count()
    

    context = {
        'category_count': category_count,
        'product_count': product_count,
        
        'username': request.user.username,
    }

    return render(request, 'admin_dash.html', context)
   

@login_required
def user_view(request):
    return render(request, 'user.html', {'user': request.user})
@login_required
def technician_view(request):
    context = {
         'username': request.user.username,
    }
    technicians = CustomUser.objects.filter(role='technician')
    return render(request, 'technician.html', context)
@login_required
def delivery_boy_view(request):
    context = {
        'username': request.user.username,
    }
    delivery_boys = CustomUser.objects.filter(role='delivery_boy')
    return render(request, 'delivery_boy.html', context)

@login_required
def device_specialist_view(request):
    context = {
        'username': request.user.username,
    }
    device_specialists = CustomUser.objects.filter(role='device_specialist')
    return render(request, 'device_specialist.html', context)
def user_login(request):
    if request.method == 'POST':
        email = request.POST['semail']
        password = request.POST['spassword']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            if user.role in ['technician', 'delivery_boy', 'device_specialist'] and not user.is_approved:
                messages.error(request, "Your account is not yet approved by the admin.")
            else:
                if user.role in ['technician', 'delivery_boy', 'device_specialist'] and user.is_approved:
                    messages.success(request, "Your account has been approved by the admin.")
                login(request, user)
                if user.role == 'admin':
                    return redirect('admin_view')
                elif user.role == 'user':
                    return redirect('user_view')
                elif user.role == 'technician':
                    return redirect('technician_view')
                elif user.role == 'delivery_boy':
                    return redirect('delivery_boy_view')
                elif user.role == 'device_specialist':
                    return redirect('device_specialist_view')
        else:
            return render(request, 'login.html', {'msg': 'Invalid email or password'})
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        # Retrieve form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        pincode = request.POST.get('pincode')  # Retrieve the selected pincode
        role = request.POST.get('role')
        password = request.POST.get('password')
        qualification = request.FILES.get('qualification', None)  # Get the uploaded file

        # Validate pincode (ensure it's within Kottayam district range)
        valid_pincodes = ['686001', '686002', '686003', '686004', '686005', '686006', '686007']  # Add more as needed
        if pincode not in valid_pincodes:
            return render(request, 'register.html', {
                'error': 'Invalid pincode selected. Please choose a valid pincode for Kottayam district.'
            })

        # Handle qualification requirement based on role
        if role in ['technician', 'delivery_boy', 'device_specialist'] and not qualification:
            return render(request, 'register.html', {
                'error': f'Qualification document is required for {role.replace("_", " ")}s.'
            })

        # Create the user
        user = CustomUser.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name,
            phone=phone,
            address=address,
            role=role,
            pincode=pincode,  # Save pincode to the database
            qualification=qualification
        )
        user.is_approved = False  # Ensure the user is not approved by default
        user.save()

        return redirect('login')
        
    return render(request, 'register.html')


def logout_view(request):
    logout(request)
    return redirect('index')

def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')
        
        if not name:
            messages.error(request, 'Category name is required.')
        elif not image:
            messages.error(request, 'Image is required.')
        else:
            category = Category(name=name, image=image)
            category.save()
            messages.success(request, 'Category added successfully.')
            return redirect('add_category')
    
    return render(request, 'add_category.html')

def accessories(request):
    categories = Category.objects.all()
    products = Product.objects.all()  # Fetch all products
    context = {
        'categories': categories,
        'products': products  # Add all products to the context
    }
    return render(request, 'accessories.html', context)
def view_category(request):
    categories = Category.objects.all()
    return render(request, 'view_category.html', {'categories': categories})

def delete_category(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
        category.delete()
        messages.success(request, 'Category deleted successfully.')
    except Category.DoesNotExist:
        messages.error(request, 'Category not found.')
    return redirect('view_category')   
def add_subcategory(request):
    if request.method == 'POST':
        category_id = request.POST.get('category')
        brand = request.POST.get('brand')
        
        if not category_id:
            messages.error(request, "Category is required.")
        elif not brand:
            messages.error(request, "Brand is required.")
        else:
            try:
                category = Category.objects.get(id=category_id)
                SubCategory.objects.create(category=category, brand=brand)
                messages.success(request, "SubCategory added successfully.")
                return redirect('add_subcategory')
            except Category.DoesNotExist:
                messages.error(request, "Invalid category selected.")
    
    categories = Category.objects.all()
    return render(request, 'add_subcategory.html', {'categories': categories})
def view_subcategory(request):
    subcategories = SubCategory.objects.select_related('category').all()
    context = {
        'subcategories': subcategories
    }
    return render(request, 'view_subcategory.html', context)
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')

        if not name:
            messages.error(request, 'Category name is required.')
        else:
            category.name = name
            if image:
                category.image = image
            category.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('view_category')

    return render(request, 'edit_category.html', {'category': category})

def edit_subcategory(request, id):
    subcategory = get_object_or_404(SubCategory, id=id)
    categories = Category.objects.all()

    if request.method == 'POST':
        category_id = request.POST.get('category')
        brand = request.POST.get('brand')

        if not category_id:
            messages.error(request, 'Category is required.')
        elif not brand:
            messages.error(request, 'Brand is required.')
        else:
            try:
                category = Category.objects.get(id=category_id)
                subcategory.category = category
                subcategory.brand = brand
                subcategory.save()
                messages.success(request, 'SubCategory updated successfully.')
                return redirect('view_subcategory')
            except Category.DoesNotExist:
                messages.error(request, 'Invalid category selected.')

    return render(request, 'edit_subcategory.html', {'subcategory': subcategory, 'categories': categories})
# Delete SubCategory View
def delete_subcategory(request,id):
    try:
        subcategory = SubCategory.objects.get(id=id)
        subcategory.delete()
        messages.success(request, 'Subcategory deleted successfully.')
    except Subcategory.DoesNotExist:
        messages.error(request, 'Subcategory not found.')
    return redirect('view_subcategory')

def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        subcategory_id = request.POST.get('subcategory')
        image = request.FILES.get('image')

        # Validation
        if not all([name, description, price, quantity, subcategory_id, image]):
            messages.error(request, "All fields are required.")
            return redirect('add_product')

        try:
            price = float(price)
            quantity = int(quantity)
        except ValueError:
            messages.error(request, "Invalid price or quantity.")
            return redirect('add_product')

        try:
            subcategory = SubCategory.objects.get(id=subcategory_id)
            product = Product(
                name=name,
                description=description,
                price=price,
                quantity=quantity,
                image=image,
                subcategory=subcategory
            )
            product.save()
            messages.success(request, "Product added successfully.")
            return redirect('add_product')
        except SubCategory.DoesNotExist:
            messages.error(request, "Invalid subcategory.")
            return redirect('add_product')

    # Handle GET request
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    return render(request, 'add_product.html', {
        'categories': categories,
        'subcategories': subcategories
    })

def view_product(request):
    products = Product.objects.all()
    return render(request, 'view_product.html', {'products': products})
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product.name = request.POST['name']
        product.description = request.POST['description']
        product.price = request.POST['price']
        product.quantity = request.POST['quantity']
        product.subcategory = SubCategory.objects.get(id=request.POST['subcategory'])

        if 'image' in request.FILES:
            product.image = request.FILES['image']
        
        product.save()
        messages.success(request, 'Product updated successfully.')
        return redirect('view_product')

    subcategories = SubCategory.objects.all()
    return render(request, 'edit_product.html', {'product': product, 'subcategories': subcategories})

def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, 'Product deleted successfully.')
    return redirect('view_product')
def get_subcategories(request):
    category_id = request.GET.get('category_id')  # Get the category_id from the request
    if category_id:
        # Filter subcategories based on the selected category
        subcategories = SubCategory.objects.filter(category_id=category_id)
        # Prepare the data to send as JSON response
        data = list(subcategories.values('id', 'brand'))  # Change 'brand' to the appropriate field
        return JsonResponse(data, safe=False)  # Return JSON response
    else:
        return JsonResponse([], safe=False) 

def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'category_products.html', context)
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Exclude the current product from the list
    related_products = Product.objects.exclude(id=product_id)
    context = {
        'product': product,
        'related_products': related_products
    }
    return render(request, 'product_detail.html', context)

def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        

        # Check if the cart item already exists
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            # If the item already exists, update the quantity
            cart_item.quantity += quantity
            cart_item.save()

        return redirect('view_cart')
@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    grand_total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'view_cart.html', {
        'cart_items': cart_items,
        'grand_total': grand_total,
    })
def update_cart(request, item_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
        cart_item.quantity = quantity
        cart_item.save()
    return redirect('view_cart')

def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('view_cart')
@login_required
def buy_now(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id)
    amount = cart_item.product.price * cart_item.quantity
    payment = Payment.objects.create(
        cart=cart_item,
        amount=amount,
        status='Pending'
    )
    
    # Redirect to a page that displays the product details from the payment
    return redirect('payment_detail', payment_id=payment.id)

@login_required
def payment_detail(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    return render(request, 'payment_detail.html', {'payment': payment})
@csrf_exempt
@login_required
def update_user_details(request):
    if request.method == 'POST':
        user = CustomUser.objects.get(pk=request.user.pk)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        user.address = request.POST.get('address', user.address)
        user.pincode = request.POST.get('pincode', user.pincode)
        user.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # sandbox or live
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})

def create_paypal_payment(request):
    if request.method == 'POST':
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": request.build_absolute_uri(reverse('paypal_execute')),
                "cancel_url": request.build_absolute_uri(reverse('payment_cancelled'))
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "Item Name",
                        "sku": "item",
                        "price": "10.00",
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": "10.00",
                    "currency": "USD"
                },
                "description": "This is the payment transaction description."
            }]
        })

        if payment.create():
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = str(link.href)
                    return redirect(approval_url)
        else:
            return render(request, 'payment_error.html', {'error': payment.error})
    return redirect('index')

def execute_paypal_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        return render(request, 'payment_success.html')
    else:
        return render(request, 'payment_error.html', {'error': payment.error})

def payment_cancelled(request):
    return render(request, 'payment_cancelled.html')


client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

def payment_details(request):
    # Fetch payment details for rendering
    payment = Payment.objects.get(id=request.GET.get('payment_id'))  # Adjust as per your logic
    return render(request, 'payment_detail.html', {'payment': payment})

def create_payment(request):
    if request.method == "POST":
        cart_id = request.POST.get('cart_id')
        cart = Cart.objects.get(id=cart_id)
        amount = cart.product.price * cart.quantity  # Calculate amount
        amount_in_paisa = int(amount * 100)  # Convert to paisa
        
        # Create Razorpay Order
        order = client.order.create(dict(
            amount=amount_in_paisa,
            currency='INR',
            payment_capture='1'
        ))
        
        # Create Payment record in DB
        payment = Payment.objects.create(
            cart=cart,
            amount=amount,
            status='Pending'
        )
        
        return JsonResponse({
            'order_id': order['id'],
            'amount': amount_in_paisa
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

def verify_payment(request):
    if request.method == "POST":
        payment_id = request.POST.get('payment_id')
        order_id = request.POST.get('order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        
        # Verify payment signature
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        try:
            client.utility.verify_payment_signature(params_dict)
            payment = Payment.objects.get(id=payment_id)
            payment.status = 'Completed'
            payment.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'fail', 'message': str(e)})
    return JsonResponse({'error': 'Invalid request'}, status=400)
@csrf_exempt
def update_payment_status(request):
    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        status = request.POST.get('status')

        try:
            payment = Payment.objects.get(id=payment_id)
            payment.status = status
            payment.save()
            return JsonResponse({'status': 'success'})
        except Payment.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Payment not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def paid_users(request):
    # Query to get all users associated with payments
    completed_payments = Payment.objects.filter(status='Paid')

    context = {
        'completed_payments': completed_payments
    }
    return render(request, 'paid_users.html', context)
    # Pass the payments to the template
  
@login_required
def technician_dashboard(request):
    if request.user.role != 'technician' or not request.user.is_approved:
        return HttpResponseForbidden("You are not allowed to access this page.")
    # Technician dashboard logic here
    return render(request, 'user.html')
    
def manage_technicians(request):
    # Filter users with 'technician' role and pending approval status
    technicians = CustomUser.objects.filter(role='technician')
    return render(request, 'manage_technicians.html', {'technicians': technicians})

def approve_technician(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if user.role == 'technician':
        user.is_approved = True
        user.save()
    return redirect('manage_technicians')

def reject_technician(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if user.role == 'technician':
        user.is_approved = False
        user.save()
    return redirect('manage_technicians')
def add_phcategory(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')
        
        if not name:
            messages.error(request, 'Category name is required.')
        elif not image:
            messages.error(request, 'Image is required.')
        else:
            category = PhoneCategory(name=name, image=image)
            category.save()
            messages.success(request, 'Category added successfully.')
            return redirect('add_phcategory')
    
    return render(request, 'add_phcategory.html')

def phone_category_list(request):
    categories = PhoneCategory.objects.all()
    return render(request, 'phone_category_list.html', {'categories': categories})
def edit_phcategory(request, category_id):
    category = get_object_or_404(PhoneCategory, id=category_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')
        
        if not name:
            messages.error(request, 'Category name is required.')
        else:
            category.name = name
            if image:
                category.image = image
            category.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('edit_phcategory', category_id=category.id)
    
    return render(request, 'edit_phcategory.html', {'category': category})
def delete_phcategory(request, category_id):
    category = get_object_or_404(PhoneCategory, id=category_id)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('phone_category_list')
    
    return render(request, 'delete_phcategory.html', {'category': category})
def add_phsubcategory(request):
    if request.method == 'POST':
        category_id = request.POST.get('category')
        brand = request.POST.get('brand')
        image = request.FILES.get('image')
        
        if not category_id:
            messages.error(request, "Category is required.")
        elif not brand:
            messages.error(request, "Brand is required.")
        elif not image:
            messages.error(request, "Image is required.")
        else:
            try:
                category = PhoneCategory.objects.get(id=category_id)
                PhoneSubCategory.objects.create(category=category, brand=brand, image=image)
                messages.success(request, "SubCategory added successfully.")
                return redirect('add_phsubcategory')
            except PhoneCategory.DoesNotExist:
                messages.error(request, "Invalid category selected.")
    
    categories = PhoneCategory.objects.all()
    return render(request, 'add_phsubcategory.html', {'categories': categories})

def list_phsubcategories(request):
    subcategories = PhoneSubCategory.objects.all()
    return render(request, 'list_phsubcategories.html', {'subcategories': subcategories})

def edit_phsubcategory(request, subcategory_id):
    subcategory = get_object_or_404(PhoneSubCategory, id=subcategory_id)
    
    if request.method == 'POST':
        category_id = request.POST.get('category')
        brand = request.POST.get('brand')
        image = request.FILES.get('image')
        
        if not category_id:
            messages.error(request, "Category is required.")
        elif not brand:
            messages.error(request, "Brand is required.")
        else:
            try:
                category = PhoneCategory.objects.get(id=category_id)
                subcategory.category = category
                subcategory.brand = brand
                if image:
                    subcategory.image = image  # Update the image only if a new one is uploaded
                subcategory.save()
                messages.success(request, "SubCategory updated successfully.")
                return redirect('list_phsubcategories')
            except PhoneCategory.DoesNotExist:
                messages.error(request, "Invalid category selected.")
    
    categories = PhoneCategory.objects.all()
    return render(request, 'edit_phsubcategory.html', {'subcategory': subcategory, 'categories': categories})

def delete_phsubcategory(request, subcategory_id):
    subcategory = get_object_or_404(PhoneSubCategory, id=subcategory_id)
    if request.method == 'POST':
        subcategory.delete()
        messages.success(request, "SubCategory deleted successfully.")
        return redirect('list_phsubcategories')
    
    return render(request, 'delete_phsubcategory.html', {'subcategory': subcategory})
def add_phone_model(request):
    if request.method == 'POST':
        subcategory_id = request.POST.get('subcategory')
        model_name = request.POST.get('model_name')

        subcategory = get_object_or_404(PhoneSubCategory, id=subcategory_id)
        PhoneModel.objects.create(subcategory=subcategory, model_name=model_name)
        return redirect('view_phone_models')

    subcategories = PhoneSubCategory.objects.all()
    return render(request, 'add_phone_model.html', {'subcategories': subcategories})
def view_phone_models(request):
    phone_models = PhoneModel.objects.all()
    return render(request, 'view_phone_model.html', {'phone_models': phone_models})
def delete_phone_model(request, model_id):
    phone_model = get_object_or_404(PhoneModel, id=model_id)
    phone_model.delete()
    return redirect('view_phone_models')
def edit_phone_model(request, model_id):
    phone_model = get_object_or_404(PhoneModel, id=model_id)
    
    if request.method == 'POST':
        model_name = request.POST.get('model_name')
        subcategory_id = request.POST.get('subcategory')

        subcategory = get_object_or_404(PhoneSubCategory, id=subcategory_id)
        phone_model.model_name = model_name
        phone_model.subcategory = subcategory
        phone_model.save()
        return redirect('view_phone_models')
    
    subcategories = PhoneSubCategory.objects.all()
    return render(request, 'edit_phone_model.html', {
        'phone_model': phone_model,
        'subcategories': subcategories
    })

def add_complaint(request):
    if request.method == 'POST':
        phone_model_id = request.POST['phone_model']
        complaint_title = request.POST['complaint_title']
        description = request.POST['description']
        expected_rate = request.POST['expected_rate']
        
        phone_model = get_object_or_404(PhoneModel, id=phone_model_id)
        Complaint.objects.create(phone_model=phone_model, complaint_title=complaint_title, description=description,expected_rate=expected_rate)
        
        return redirect('complaint_list')
    
    phone_models = PhoneModel.objects.all()
    return render(request, 'add_complaint.html', {'phone_models': phone_models})
def complaint_list(request):
    complaints = Complaint.objects.all()
    return render(request, 'complaint_list.html', {'complaints': complaints})
def delete_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    
    if request.method == 'POST':
        complaint.delete()
        return redirect('complaint_list')
def edit_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    
    if request.method == 'POST':
        phone_model_id = request.POST['phone_model']
        complaint_title = request.POST['complaint_title']
        description = request.POST['description']
        expected_rate = request.POST['expected_rate']
        
        phone_model = get_object_or_404(PhoneModel, id=phone_model_id)
        
        complaint.phone_model = phone_model
        complaint.complaint_title = complaint_title
        complaint.description = description
        complaint.expected_rate = expected_rate
        complaint.save()
        
        return redirect('complaint_list')
    
    phone_models = PhoneModel.objects.all()
    return render(request, 'edit_complaint.html', {'complaint': complaint, 'phone_models': phone_models})
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = CustomUser.objects.get(email=email)  # Use CustomUser
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = request.build_absolute_uri(f'/reset_password/{uid}/{token}/')

            message = render_to_string('reset_password_email.html', {
                'user': user,
                'reset_link': reset_link,
            })

            send_mail(
                'Password Reset Request',
                message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            return render(request, 'forgot_password.html', {'message': 'A reset link has been sent to your email address.'})
        except CustomUser.DoesNotExist:  # Use CustomUser
            return render(request, 'forgot_password.html', {'error': 'Email does not exist'})
    return render(request, 'forgot_password.html')

def reset_password(request, uidb64, token):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = CustomUser.objects.get(pk=uid)  # Use CustomUser
                if default_token_generator.check_token(user, token):
                    user.set_password(password)  # Use set_password to hash the password
                    user.save()
                    return redirect('login')
                else:
                    return render(request, 'reset_password.html', {'error': 'Invalid token'})
            except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):  # Use CustomUser
                return render(request, 'reset_password.html', {'error': 'Invalid link'})
        else:
            return render(request, 'reset_password.html', {'error': 'Passwords do not match'})
    return render(request, 'reset_password.html')
def download_qualification(request, user_id):
    # Fetch the user based on user_id
    user = get_object_or_404(CustomUser, id=user_id)

    if user.qualification:
        # Construct the full file path
        file_path = user.qualification.path
        
        # Read the file and create a response
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{user.qualification.name}"'
            return response
    else:
        raise PermissionDenied("Qualification document not found.")

def repair_view(request):
    # Fetch active categories, subcategories, models, and complaints for the form
    categories = PhoneCategory.objects.filter(status='active')
    subcategories = PhoneSubCategory.objects.filter(category__status='active')
    phone_models = PhoneModel.objects.filter(subcategory__category__status='active')
    complaints = Complaint.objects.filter(phone_model__subcategory__category__status='active', phone_model__in=phone_models)

    if request.method == 'POST':
        # Get the IDs from the form submission
        phone_category_id = request.POST.get('phone_category')
        phone_subcategory_id = request.POST.get('phone_subcategory')
        phone_model_id = request.POST.get('phone_model')
        phone_complaint_id = request.POST.get('phone_complaint')
        expected_rate = request.POST.get('expected_rate') 
        pickup_date = request.POST.get('pickup_date')
        phone_number = request.POST.get('phone_number')
        issue_description = request.POST.get('issue_description')
        pickup_address = request.POST.get('pickup_address')
        terms_accepted = request.POST.get('terms_accepted') == 'on'
        
        # Retrieve the related objects using the ForeignKey relationships
        phone_category = get_object_or_404(PhoneCategory, id=phone_category_id)
        phone_subcategory = get_object_or_404(PhoneSubCategory, id=phone_subcategory_id)
        phone_model = get_object_or_404(PhoneModel, id=phone_model_id)
        phone_complaint = get_object_or_404(Complaint, id=phone_complaint_id)
        
        # Create a new ServiceRequest object and save it to the database
        service_request = ServiceRequest(
              # Assuming the user is logged in
            phone_category=phone_category,
            phone_subcategory=phone_subcategory,
            phone_model=phone_model,
            phone_complaint=phone_complaint,
            expected_rate=expected_rate,
            pickup_date=pickup_date,
            phone_number=phone_number,
            issue_description=issue_description,
            pickup_address=pickup_address,
            terms_accepted=terms_accepted,
            status='pending',  # Default value
            amount=0.00,       # Default value
            delivery_date=None # Default value
        )
        service_request.save()
        
        # Redirect to a success page (or any other page)
        return redirect('repair_status')
    
    # Render the form with context data
    return render(request, 'repair.html', {
        'categories': categories,
        'subcategories': subcategories,
        'phone_models': phone_models,
        'complaints': complaints
    })
def repair_status(request):
    service_requests = ServiceRequest.objects.all()
    return render(request, 'repair_status.html', {'service_requests': service_requests})
    
def phone_category_view(request):
    categories = PhoneCategory.objects.filter(status='active')  # Fetch active categories
    return render(request, 'categories.html', {'categories': categories})
def repairs_view(request):
    subcategories  = PhoneSubCategory.objects.filter(status='active')  # Fetch active categories
    return render(request, 'repair.html', {'subcategories ': subcategories })
def get_subcategory(request):
    category_id = request.GET.get('category_id')
    subcategories = PhoneSubCategory.objects.filter(category_id=category_id)
    data = [{'id': subcategory.id, 'name': subcategory.brand} for subcategory in subcategories]
    return JsonResponse(data, safe=False)

def get_models(request):
    category_id = request.GET.get('category_id')
    subcategories = PhoneSubCategory.objects.filter(category_id=category_id)
    models = PhoneModel.objects.filter(subcategory__in=subcategories)
    data = [{'id': model.id, 'name': model.model_name} for model in models]
    return JsonResponse(data, safe=False)

def get_complaints(request):
    category_id = request.GET.get('category_id')
    subcategories = PhoneSubCategory.objects.filter(category_id=category_id)
    models = PhoneModel.objects.filter(subcategory__in=subcategories)
    complaints = Complaint.objects.filter(phone_model__in=models)
    data = [{'id': complaint.id, 'complaint_title': complaint.complaint_title} for complaint in complaints]
    return JsonResponse(data, safe=False)

def create_service_request(request):
    
    if request.method == 'POST':
        phone_category = request.POST.get('phone_category')
        phone_subcategory = request.POST.get('phone_subcategory')
        phone_model = request.POST.get('phone_model')
        phone_complaint = request.POST.get('phone_complaint')
        pickup_date = request.POST.get('pickup_date')
        phone_number = request.POST.get('phone_number')
        issue_description = request.POST.get('issue_description')
        pickup_address = request.POST.get('pickup_address')
        terms_accepted = request.POST.get('terms_accepted') == 'on'
        
        # Create a new ServiceRequest object and save it to the database
        service_request = ServiceRequest(
            phone_category=phone_category,
            phone_subcategory=phone_subcategory,
            phone_model=phone_model,
            phone_complaint=phone_complaint,
            pickup_date=pickup_date,
            phone_number=phone_number,
            issue_description=issue_description,
            pickup_address=pickup_address,
            terms_accepted=terms_accepted,
            status='pending',  # Default value
            amount=0.00,       # Default value
            delivery_date=None # Default value
        )
        service_request.save()
        
        # Redirect to a success page (or any other page)
        return redirect('service_request_success')
    
    return render(request, 'service_request_form.html')
def service_request_success(request):
    return render(request, 'service_request_success.html')
def get_service_request_data(request, service_request_id):
    service_request = get_object_or_404(ServiceRequest, id=service_request_id)
    data = {
        'id': service_request.id,
        'status': service_request.status,
        'amount': str(service_request.amount),
        'delivery_date': service_request.delivery_date.strftime('%Y-%m-%d') if service_request.delivery_date else ''
    }
    return JsonResponse(data)

# Update Service Request
def update_service_request(request):
    if request.method == 'POST':
        service_request_id = request.POST.get('service_request_id')
        service_request = get_object_or_404(ServiceRequest, id=service_request_id)

        service_request.status = request.POST.get('status')
        service_request.amount = request.POST.get('amount')
        service_request.delivery_date = request.POST.get('delivery_date')

        service_request.save()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False})
def service_requests(request):
    service_requests = ServiceRequest.objects.all()
    return render(request, 'service_requests.html', {'service_requests': service_requests})
def terms_and_conditions(request):
    terms = TermsAndConditions.objects.last()  # Get the most recent terms and conditions
    return render(request, 'terms_and_conditions.html', {'terms': terms})
@csrf_exempt
def submit_terms(request):
    if request.method == 'POST':
        content = request.POST.get('terms_content')
        TermsAndConditions.objects.create(content=content)
        return redirect('terms_and_conditions')  # Redirect to the terms and conditions page
    return render(request, 'manage_terms.html')
def manage_terms_and_conditions(request):
    return render(request, 'manage_terms.html')
def get_expected_rate(request):
    complaint_id = request.GET.get('complaint_id')
    if complaint_id:
        try:
            complaint = Complaint.objects.get(id=complaint_id)
            expected_rate = complaint.expected_rate  # Assuming your Complaint model has this field
            return JsonResponse({'expected_rate': expected_rate})
        except Complaint.DoesNotExist:
            return JsonResponse({'error': 'Complaint not found'}, status=404)
    return JsonResponse({'error': 'Invalid request'}, status=400)

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

def create_order(request, id):
    service_request = get_object_or_404(ServiceRequest, id=id)
    
    # Create an order with Razorpay
    amount = service_request.amount  # Amount in paise
    currency = 'INR'
    
    order = client.order.create(dict(
        amount=int(amount * 100),
        currency=currency,
        payment_capture='1'  # Auto capture the payment
    ))
    
    # Save order information to the Payments model
    Payments.objects.create(
        user=request.user,  # Assuming user is logged in
        service_request=service_request,
        razorpay_order_id=order['id'],
        amount=amount / 100,  # Convert back to rupees
        status='paid'
    )
    
    return render(request, 'razorpay_checkout.html', {
        'order_id': order['id'],
        'amount': amount,
        'currency': currency
    })

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

@csrf_exempt
def razorpay_webhook(request):
    if request.method == 'POST':
        webhook_data = json.loads(request.body.decode('utf-8'))
        event = request.META.get('HTTP_X_RAZORPAY_EVENT')

        if event == 'payment.captured':
            data = webhook_data['payload']['payment']['entity']
            razorpay_order_id = data['order_id']
            razorpay_payment_id = data['id']
            
            try:
                payment = Payments.objects.get(razorpay_order_id=razorpay_order_id)
                payment.razorpay_payment_id = razorpay_payment_id
                payment.status = 'completed'
                payment.save()
                return JsonResponse({'status': 'success'})
            except Payments.DoesNotExist:
                return JsonResponse({'status': 'success', 'message': 'Payment record not found'}, status=400)
    
    return JsonResponse({'status': 'failure'}, status=400)

model = joblib.load('chatbot_model.pkl')

def chatbot_view(request):
    form = ComplaintForm(request.POST or None)
    response = ''
    if form.is_valid():
        complaint = form.cleaned_data['complaint']
        prediction = model.predict([complaint])[0]
        if prediction == 'Yes':
            response = "Solution: 1. Turn off the phone. 2. Remove the case."
        else:
            response = "Please visit the shop for further assistance."
    return render(request, 'myapp/chatbot.html', {'form': form, 'response': response})
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from io import BytesIO
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch
from io import BytesIO
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from datetime import datetime
import os

def download_receipt(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)

    content = []
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['Normal']
    bold_style = styles['Normal']
    bold_style.fontName = 'Helvetica-Bold'

    # Add the MobiCare logo
    logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'images/logo.png')
    content.append(Image(logo_path, width=1.3*inch, height=1.3*inch))
    
    # Title Section (Aligned with the logo)
    content.append(Paragraph("<strong>MobiCare Payment Receipt</strong>", title_style))
    content.append(Spacer(1, 12))
    content.append(Paragraph(f"Receipt ID: {payment.id}", normal_style))
    content.append(Paragraph(f"Date: {current_date}", normal_style))
    content.append(Spacer(1, 12))

    # Product Details
    product_details = [
        [Paragraph("<strong>Product Details</strong>", bold_style), ''],
        ['Product Name:', payment.cart.product.name],
        ['Price:', f'Rs {payment.cart.product.price}'],
        ['Quantity:', payment.cart.quantity],
        ['Total Amount:', f'Rs {payment.amount}'],
        ['Status:', payment.status],
    ]

    table = Table(product_details, colWidths=[2 * inch, 4 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    content.append(table)
    content.append(Spacer(1, 12))

    # User Details
    user_details = [
        [Paragraph("<strong>User Details</strong>", bold_style), ''],
        ['Name:', f'{payment.cart.user.first_name} {payment.cart.user.last_name}'],
        ['Address:', payment.cart.user.address],
        ['Phone Number:', payment.cart.user.phone],
        ['PIN Number:', payment.cart.user.pincode],
    ]

    user_table = Table(user_details, colWidths=[2 * inch, 4 * inch])
    user_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    content.append(user_table)
    content.append(Spacer(1, 12))

    # Total Amount Section with underline
    content.append(Paragraph("<strong>____________________________________</strong>", normal_style))
    content.append(Spacer(1, 12))
    content.append(Paragraph(f"<strong>Total Amount Paid: Rs {payment.amount}</strong>", bold_style))
    content.append(Spacer(1, 12))
    content.append(Paragraph("<strong>____________________________________</strong>", normal_style))
    content.append(Spacer(1, 12))

    # Thank You Note
    content.append(Paragraph("Thank you for your purchase!", normal_style))
    content.append(Spacer(1, 12))

    # Add borders around the receipt content (optional, to make it resemble a printed bill)
    table_frame = Table([[content]], colWidths=[7.5 * inch])
    table_frame.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 2, colors.black),  # Outer border
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    # Build the PDF
    pdf.build([table_frame])

    # Return the PDF response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment.id}.pdf"'
    return response

def add_to_wishlist(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        if created:
            # Optionally, you could add a message here indicating the product was added.
            pass
        return redirect('product_detail', product_id=product_id)
    else:
        # Redirect to login if the user is not authenticated
        return redirect('login')

def remove_from_wishlist(request, product_id):
    if request.user.is_authenticated:
        Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
        # Optionally, add a message indicating the product was removed.
        return redirect('product_detail', product_id=product_id)
    else:
        return redirect('login')

def wishlist_view(request):
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user)
        return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})
    else:
        return redirect('login')
def feedback_view(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        emoji = request.POST.get('emoji')
        
        if message and emoji:  # Simple validation
            feedback = Feedback(user=request.user, message=message, emoji=emoji)
            feedback.save()
            return redirect('accessories')  # Redirect to a success page or feedback list
    return render(request, 'feedback.html')

def feedback_success(request):
    return render(request, 'feedback_success.html')

def feedback_list_view(request):
    feedbacks = Feedback.objects.all()
    return render(request, 'feedback_list.html', {'feedbacks': feedbacks})
def special_days_view(request):
    today = datetime.now().date()
    special_days = {
        'Onam': {'date': today, 'emoji': '🎉'},  # Today's date for Onam
        'Diwali': {'date': datetime(today.year, 11, 12).date(), 'emoji': '🪔'},
        # Add more special days here
    }

    emojis = []
    for day, info in special_days.items():
        if today == info['date']:
            emojis.append(f"{day}: {info['emoji']}")

    return render(request, 'special_days.html', {'emojis': emojis})

def product_filter(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_name = data.get('productName', '').strip()
        min_price = data.get('minPrice', 0)
        max_price = data.get('maxPrice', float('inf'))

        filtered_products = Product.objects.filter(
            name__icontains=product_name,
            price__gte=min_price,
            price__lte=max_price,
            status='active'  # Filter by active status if needed
        ).values('name', 'description', 'price', 'image')  # Return the fields you need
        

        return JsonResponse(list(filtered_products), safe=False)
def edit_profile(request):
    user = request.user
    
    if request.method == 'POST':
        user.username = request.POST['username']
        user.email = request.POST['email']
        user.phone = request.POST['phone']
        user.address = request.POST['address']
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('user_view')  # Redirect to profile page after saving
    
    return render(request, 'user.html', {'user': user})

def order_history(request):
    # Fetch all payments for the logged-in user, along with related cart and product information
    user_payments = Payment.objects.filter(cart__user=request.user).select_related('cart__product')

    # Create a set to store unique products based on the product id
    unique_payments = []
    seen_products = set()

    for payment in user_payments:
        product_id = payment.cart.product.id
        if product_id not in seen_products:
            unique_payments.append(payment)
            seen_products.add(product_id)

    return render(request, 'order_history.html', {'payments': unique_payments})

def technician_profile(request, technician_id):
    # Fetch the technician object or return a 404 if not found
    technician = get_object_or_404(CustomUser, id=technician_id)
    return render(request, 'your_template.html', {'technician': technician})
def edit_technician(request, user_id):
    technician = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        technician.username = request.POST['username']
        technician.email = request.POST['email']
        technician.phone = request.POST['phone']
        technician.address = request.POST['address']
        
        # Check for file upload
        if 'qualification' in request.FILES:
            technician.qualification = request.FILES['qualification']
        
        technician.save()
        return redirect('technician_profile', technician_id=user_id)
    
    return render(request, 'technician.html', {'user': technician})

def feedback_lists(request):
    feedbacks = Feedback.objects.select_related('user').all()  # Use select_related for optimization
    return render(request, 'feedback_lists.html', {'feedbacks': feedbacks})
def completed_service_requests(request):
    # Filter service requests where the status is 'completed'
    completed_requests = ServiceRequest.objects.filter(status='completed')
    
    context = {
        'completed_requests': completed_requests
    }
    
    return render(request, 'completed_service.html', context)
def service_requests_list(request):
    service_requests = ServiceRequest.objects.all()  # Fetch all service requests
    context = {
        'service_requests': service_requests
    }
    return render(request, 'service_requests_list.html', context)

def history_order(request):
    user_payments = Payment.objects.filter(cart__user=request.user).select_related('cart__product')

    # Create a set to store unique products based on the product id
    unique_payments = []
    seen_products = set()

    for payment in user_payments:
        product_id = payment.cart.product.id
        if product_id not in seen_products:
            unique_payments.append(payment)
            seen_products.add(product_id)

    return render(request, 'history_order.html', {'payments': unique_payments})
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Here you would typically save the message to a database or send an email
        send_mail(
            f'Contact Form Submission from {name}',
            message,
            email,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )

        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact')  # Redirect back to the contact page

    return render(request, 'contact.html')
def manage_device_specialists(request):
    device_specialists = CustomUser.objects.filter(role='device_specialist')
    return render(request, 'manage_devicespecialist.html', {'specialists': device_specialists})

def approve_device_specialist(request, user_id):
    specialist = CustomUser.objects.get(id=user_id, role='device_specialist')
    specialist.is_approved = True
    specialist.save()
    return redirect('manage_device_specialists')

def reject_device_specialist(request, user_id):
    specialist = CustomUser.objects.get(id=user_id, role='device_specialist')
    specialist.is_approved = False
    specialist.save()
    return redirect('manage_device_specialists')
def manage_delivery_boys(request):
    delivery_boys = CustomUser.objects.filter(role='delivery_boy')
    return render(request, 'manage_deliveryboy.html', {'delivery_boys': delivery_boys})

def approve_delivery_boy(request, user_id):
    delivery_boy = CustomUser.objects.get(id=user_id, role='delivery_boy')
    delivery_boy.is_approved = True
    delivery_boy.save()
    return redirect('manage_delivery_boys')

def reject_delivery_boy(request, user_id):
    delivery_boy = CustomUser.objects.get(id=user_id, role='delivery_boy')
    delivery_boy.is_approved = False
    delivery_boy.save()
    return redirect('manage_delivery_boys')
@login_required
def delivery_boy_profile(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("delivery_boy_profile")
        else:
            messages.error(request, "Error updating profile.")
    else:
        form = EditProfileForm(instance=request.user)
    
    return render(request, "delivery_boy_profile.html", {"form": form, "user": request.user})
def assign_delivery_boy(request, id):
    # Get the delivery boy user by ID
    delivery_boy = get_object_or_404(CustomUser, id=id, role='delivery_boy')

    # Check if the delivery boy is approved
    if not delivery_boy.is_approved:
        messages.error(request, "This delivery boy is not approved yet!")
        return redirect('manage_delivery_boys')  # Replace with the correct list view name

    if request.method == "POST":
        assigned_area = request.POST.get('assigned_area')
        delivery_boy.assigned_area = assigned_area
        delivery_boy.save()

        messages.success(request, f"Assigned {assigned_area} to {delivery_boy.username}")
        return redirect('manage_delivery_boys')  # Replace with the correct list view name

    return render(request, 'assign_delivery_boy.html', {'delivery_boy': delivery_boy})
def get_all_delivery_boy_details(request):
    if request.method == "GET":
        # Fetch all delivery boys
        delivery_boys = CustomUser.objects.filter(role="delivery_boy")
        data = [
            {
                "username": boy.username,
                "email": boy.email,
                "phone": boy.phone,
                "assigned_area": boy.assigned_area or "Not Assigned",
                "status": boy.get_status_display(),
            }
            for boy in delivery_boys
        ]
        return JsonResponse({"success": True, "data": data})
def delete_delivery_boy(request, delivery_boy_id):
    # Fetch the delivery boy object or return 404
    delivery_boy = get_object_or_404(CustomUser, id=delivery_boy_id, role='delivery_boy')

    # Perform the deletion
    delivery_boy.delete()

    # Show a success message
    messages.success(request, "Delivery boy deleted successfully.")

    # Redirect back to the manage delivery agents page
    return redirect('manage_delivery_boys')

def assigned_orders(request):
    if request.user.role == 'delivery_boy' and request.user.assigned_area:
        users = CustomUser.objects.filter(role='user', pincode=request.user.assigned_area)
        orders = Payment.objects.filter(cart__user__in=users, status='Paid').select_related('cart__product')

        if request.method == 'POST':
            otp = request.POST.get('otp')
            delivered_at = request.POST.get('delivered_at')
            payment_id = request.POST.get('payment_id')

            # Debugging to check if payment_id is correctly passed
            print(f"Received payment_id: {payment_id}")

            if payment_id:  # Check if payment_id is not empty
                try:
                    payment = Payment.objects.get(id=payment_id)
                    payment.otp = otp
                    payment.delivered_at = delivered_at
                    payment.save()

                    messages.success(request, "Order updated successfully.")
                except Payment.DoesNotExist:
                    messages.error(request, "Payment order not found.")
            else:
                messages.error(request, "Invalid payment ID.")

            return redirect('assigned_orders')

    else:
        users = CustomUser.objects.none()
        orders = Payment.objects.none()

    context = {
        'users': users,
        'orders': orders,
    }
    return render(request, 'assigned_orders.html', context)

@csrf_exempt
def update_order_status(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            payment_id = data.get("payment_id")
            new_status = data.get("order_status")

            payment = Payment.objects.get(id=payment_id)
            payment.order_status = new_status

            # If status is "Out of Delivery", generate OTP
            if new_status == "Out of Delivery":
                payment.generate_otp()

            payment.save()

            return JsonResponse({"success": True, "otp": payment.otp if new_status == "Out of Delivery" else None})

        except Payment.DoesNotExist:
            return JsonResponse({"success": False, "error": "Payment not found"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        payment_id = request.POST.get('payment_id')
        
        try:
            payment = Payment.objects.get(id=payment_id)
            
            # Check if the entered OTP matches the stored OTP
            if payment.otp == entered_otp:
                return JsonResponse({'status': 'success', 'message': 'OTP is correct'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid OTP'})
        except Payment.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Payment not found'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
@csrf_exempt  # Allow AJAX requests without CSRF protection (for development)
def update_location(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            payment_id = data.get('payment_id')
            latitude = data.get('latitude')
            longitude = data.get('longitude')

            payment = Payment.objects.get(id=payment_id)
            payment.latitude = latitude
            payment.longitude = longitude
            payment.save()

            return JsonResponse({'success': True})
        except Payment.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Payment not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})
@login_required
def edit_specialist_profile(request):
    if request.method == 'POST':
        user = request.user
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.address = request.POST.get('address')

        # Handle qualification file upload
        if 'qualification' in request.FILES:
            user.qualification = request.FILES['qualification']

        user.save()
                # ✅ Prevent logout by updating session authentication
        update_session_auth_hash(request, user)
        messages.success(request, "Profile updated successfully!")
        return redirect('/?profile_modal=open')  # Redirect with a query parameter

    return redirect('/')
def sell_old_phone(request):
    return render(request, 'sell_old_phone.html')
def add_old_phone_category(request):
    if request.method == "POST":
        category_name = request.POST.get("category_name")
        image = request.FILES.get("category_image")

        if category_name:
            OldPhoneCategory.objects.create(name=category_name, image=image)  # Save image
            messages.success(request, "Old Phone Category added successfully!")
            return redirect("add_old_phone_category")
        else:
            messages.error(request, "Category name cannot be empty!")

    return render(request, "add_old_phone_category.html")
def view_old_phone_categories(request):
    categories = OldPhoneCategory.objects.all()  # Fetch all categories
    return render(request, 'view_old_phone_categories.html', {'categories': categories})
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import OldPhoneCategory, OldPhoneSubCategory
import re  # Import regex module for validation

def add_old_phone_subcategory(request):
    categories = OldPhoneCategory.objects.all()

    if request.method == "POST":
        category_id = request.POST.get("category")
        subcategory_name = request.POST.get("subcategory").strip()

        if not category_id:
            messages.error(request, "⚠️ Please select a category.")
            return redirect('add_old_phone_subcategory')

        if not subcategory_name:
            messages.error(request, "⚠️ SubCategory name cannot be empty.")
            return redirect('add_old_phone_subcategory')

        if not re.match(r"^[a-zA-Z\s]+$", subcategory_name):  # Check if only alphabets and spaces are allowed
            messages.error(request, "⚠️ SubCategory name must contain only letters.")
            return redirect('add_old_phone_subcategory')

        try:
            category = OldPhoneCategory.objects.get(id=category_id)
        except OldPhoneCategory.DoesNotExist:
            messages.error(request, "⚠️ Selected category does not exist.")
            return redirect('add_old_phone_subcategory')

        if OldPhoneSubCategory.objects.filter(category=category, name=subcategory_name).exists():
            messages.error(request, "⚠️ This SubCategory already exists.")
            return redirect('add_old_phone_subcategory')

        OldPhoneSubCategory.objects.create(category=category, name=subcategory_name)
        messages.success(request, "✅ SubCategory added successfully!")
        return redirect('add_old_phone_subcategory')

    return render(request, 'add_old_phone_subcategory.html', {'categories': categories})

def delete_old_phone_category(request, pk):
    category = get_object_or_404(OldPhoneCategory, pk=pk)
    category.delete()
    return redirect('view_old_phone_categories') 
def edit_old_phone_category(request, pk):
    category = get_object_or_404(OldPhoneCategory, id=pk)


    if request.method == "POST":
        data = json.loads(request.body)
        category_name = data.get("category_name", "").strip()

        # Server-side validation
        if not category_name:
            return JsonResponse({"success": False, "error": "Category name cannot be empty."})

        if not re.match(r"^[A-Za-z\s]+$", category_name):
            return JsonResponse({"success": False, "error": "Category name must contain only alphabetic characters."})

        # Check for duplicate category names
        if OldPhoneCategory.objects.filter(name__iexact=category_name).exclude(id=category.id).exists():
            return JsonResponse({"success": False, "error": "A category with this name already exists."})

        category.name = category_name
        category.save()
        return JsonResponse({"success": True})

    return render(request, "edit_old_phone_category.html", {"category": category})
def view_old_phone_subcategories(request):
    subcategories = OldPhoneSubCategory.objects.select_related('category').all()
    return render(request, 'view_old_phone_subcategories.html', {'subcategories': subcategories})
def delete_old_phone_subcategory(request, pk):
    subcategory = get_object_or_404(OldPhoneSubCategory, id=pk)
    subcategory.delete()
    messages.success(request, "✅ SubCategory deleted successfully!")
    return redirect('view_old_phone_subcategory')
def edit_old_phone_subcategory(request, pk):
    subcategory = get_object_or_404(OldPhoneSubCategory, pk=pk)
    
    if request.method == 'POST':
        new_name = request.POST.get('subcategory_name').strip()
        
        if not new_name:
            messages.error(request, "⚠️ SubCategory name cannot be empty.")
            return redirect('edit_old_phone_subcategory', pk=pk)

        if not re.match(r"^[a-zA-Z\s]+$", new_name):
            messages.error(request, "⚠️ SubCategory name must contain only letters.")
            return redirect('edit_old_phone_subcategory', pk=pk)

        subcategory.name = new_name
        subcategory.save()
        messages.success(request, "✅ SubCategory updated successfully!")
        return redirect('view_old_phone_subcategory')

    return render(request, 'edit_old_phone_subcategory.html', {'subcategory': subcategory})
def add_old_phone_model(request):
    subcategories = OldPhoneSubCategory.objects.all()
    
    if request.method == "POST":
        name = request.POST.get("name").strip()
        subcategory_id = request.POST.get("subcategory")
        
        if not name:
            messages.error(request, "⚠️ Model name cannot be empty.")
            return redirect('add_old_phone_model')
        
        if not subcategory_id:
            messages.error(request, "⚠️ Please select a subcategory.")
            return redirect('add_old_phone_model')
        
        subcategory = OldPhoneSubCategory.objects.get(id=subcategory_id)
        OldPhoneModel.objects.create(name=name, subcategory=subcategory)
        messages.success(request, "✅ Model added successfully!")
        return redirect('view_old_phone_models')
    
    return render(request, 'add_old_phone_model.html', {'subcategories': subcategories})

def view_old_phone_models(request):
    models = OldPhoneModel.objects.select_related('subcategory').all()
    return render(request, 'view_old_phone_models.html', {'models': models})

def edit_old_phone_model(request, pk):
    model_instance = get_object_or_404(OldPhoneModel, pk=pk)
    subcategories = OldPhoneSubCategory.objects.all()
    
    if request.method == "POST":
        name = request.POST.get("name").strip()
        subcategory_id = request.POST.get("subcategory")
        
        if not name:
            messages.error(request, "⚠️ Model name cannot be empty.")
            return redirect('edit_old_phone_model', pk=pk)
        
        if not subcategory_id:
            messages.error(request, "⚠️ Please select a subcategory.")
            return redirect('edit_old_phone_model', pk=pk)
        
        subcategory = OldPhoneSubCategory.objects.get(id=subcategory_id)
        model_instance.name = name
        model_instance.subcategory = subcategory
        model_instance.save()
        messages.success(request, "✅ Model updated successfully!")
        return redirect('view_old_phone_models')

    return render(request, 'edit_old_phone_model.html', {'model': model_instance, 'subcategories': subcategories})

def delete_old_phone_model(request, pk):
    model_instance = get_object_or_404(OldPhoneModel, pk=pk)
    model_instance.delete()
    messages.success(request, "✅ Model deleted successfully!")
    return redirect('view_old_phone_models')
@login_required
def sell_request(request):
    user = request.user  # Get the logged-in user
    context = {
        'user_name': user.first_name,
        'phone_number': user.phone,
        'phone_categories': PhoneCategory.objects.all(),  # If you have categories
    }
    return render(request, 'sell_request.html', context)



def image_search(request):
    return render(request, 'image_search.html')
@login_required
def sell_request(request):
    user = request.user  # Get the logged-in user

    if request.method == "POST":
        user_name = request.POST.get("user_name")
        phone_number = request.POST.get("phone_number")
        imei_number = request.POST.get("imei_number")
        phone_category = request.POST.get("phone_category")
        phone_subcategory = request.POST.get("phone_subcategory")
        phone_model = request.POST.get("phone_model")
        phone_condition = request.POST.get("phone_condition")
        pickup_date = request.POST.get("pickup_date")
        pincode = request.POST.get("pincode")
        issue_description = request.POST.get("issue_description", "")
        pickup_address = request.POST.get("pickup_address")
        phone_images = request.FILES.getlist("phone_images")  # Multiple images

        # Save the form data to the database
        phone_repair_request = PhoneRepairRequest.objects.create(
            user_name=user_name,
            phone_number=phone_number,
            imei_number=imei_number,
            phone_category=phone_category,
            phone_subcategory=phone_subcategory,
            phone_model=phone_model,
            phone_condition=phone_condition,
            pickup_date=pickup_date,
            pincode=pincode,
            issue_description=issue_description,
            pickup_address=pickup_address,
        )

        # Handle multiple image uploads
        for image in phone_images:
            phone_repair_request.phone_images.save(image.name, image)

        messages.success(request, "Your request has been submitted successfully!")
        return redirect("user_requests")  # Change to your success page URL name

    context = {
        'user_name': user.first_name,
        'phone_number': user.phone,
        'phone_categories': PhoneCategory.objects.all(),  # If you have categories
    }
    return render(request, 'sell_request.html', context)
@login_required
def user_requests(request):
    user = request.user  # Get the logged-in user
    user_requests = PhoneRepairRequest.objects.filter(phone_number=user.phone)

    context = {
        'user_requests': user_requests,
    }
    return render(request, 'user_requests.html', context)
def technician_list(request):
    active_technicians = CustomUser.objects.filter(role='technician', status='active')
    return render(request, 'accessories.html', {'active_technicians': active_technicians})