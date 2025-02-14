from django.db import models
from django.conf import settings
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
import random
STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
]

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    pincode = models.CharField(max_length=6)
    ROLE_CHOICES = [
        ('technician', 'Technician'),
        ('user', 'User'),
        ('admin', 'Admin'),
        ('delivery_boy', 'Delivery Boy'),
        ('device_specialist', 'Device Specialist'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_approved = models.BooleanField(default=False)
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    qualification = models.FileField(upload_to='qualifications/', blank=True, null=True)
    assigned_area = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return self.brand


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    quantity = models.PositiveIntegerField()
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return self.name
    
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
class Payment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]
    
    ORDER_STATUS_CHOICES = [
        ('Order Confirmed', 'Order Confirmed'),
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Out of Delivery', 'Out of Delivery'),  # Add this option
    ]

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Order Confirmed')
    created_at = models.DateTimeField(auto_now_add=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)# New OTP field
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)



    def generate_otp(self):
        """Generate a 6-digit OTP and save it to the model."""
        self.otp = str(random.randint(100000, 999999))
        self.save()

    def __str__(self):
        return f"Payment {self.id} - {self.cart.user.username} - {self.status} - {self.order_status}"
    
STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
]

class PhoneCategory(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='phone_categories/')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return self.name


class PhoneSubCategory(models.Model):
    category = models.ForeignKey('PhoneCategory', on_delete=models.CASCADE)
    brand = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    image = models.ImageField(upload_to='subcategory_images/', null=True, blank=True)

    def __str__(self):
        return self.brand


class PhoneModel(models.Model):
    subcategory = models.ForeignKey(PhoneSubCategory, on_delete=models.CASCADE)
    model_name = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return self.model_name


class Complaint(models.Model):
    phone_model = models.ForeignKey(PhoneModel, on_delete=models.CASCADE)
    complaint_title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    expected_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  

    def __str__(self):
        return f"{self.complaint_title} - {self.phone_model.model_name}"

class ServiceRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('on_working', 'On Working'),
        ('completed', 'Completed'),
    )

   
    phone_category = models.ForeignKey(PhoneCategory, on_delete=models.CASCADE)
    phone_subcategory = models.ForeignKey(PhoneSubCategory, on_delete=models.CASCADE)
    phone_model = models.ForeignKey(PhoneModel, on_delete=models.CASCADE)
    phone_complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    expected_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pickup_date = models.DateField()
    phone_number = models.CharField(max_length=15)
    issue_description = models.TextField()
    pickup_address = models.TextField()
    terms_accepted = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    delivery_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.phone_category.name} - {self.phone_model.model_name} ({self.status})"
class TermsAndConditions(models.Model):
    content = models.TextField()

    def __str__(self):
        return f"Terms and Conditions (ID: {self.id})"
class Payments(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=100)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=(('Success', 'Success'), ('completed', 'Completed')))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}"
class CalendarEvent(models.Model):
    title = models.CharField(max_length=255)
    event_date = models.DateField()

    def __str__(self):
        return self.title
class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)  # Ensure 'Product' is defined or imported

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username}'s Wishlist - {self.product.name}"
class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    emoji = models.CharField(max_length=10)  # Store emoji as a string
    created_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"Feedback from {self.user.username}: {self.emoji}"
class OldPhoneCategory(models.Model):  # Changed table name to "old_phone_category"
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='old_phone_categories/', blank=True, null=True)

    class Meta:
        db_table = "old_phone_category"  # Custom table name

    def __str__(self):
        return self.name
class OldPhoneSubCategory(models.Model):
    category = models.ForeignKey(OldPhoneCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "old_phone_subcategory"  # Custom table name

    def __str__(self):
        return self.name
class OldPhoneModel(models.Model):
    name = models.CharField(max_length=255)
    subcategory = models.ForeignKey('OldPhoneSubCategory', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
class PhoneRepairRequest(models.Model):
    user_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    imei_number = models.CharField(max_length=15, unique=True)
    phone_category = models.CharField(max_length=255)
    phone_subcategory = models.CharField(max_length=255)
    phone_model = models.CharField(max_length=255)
    phone_condition = models.CharField(max_length=50, choices=[
        ('Like New', 'Like New'),
        ('Good', 'Good'),
        ('Average', 'Average'),
        ('Needs Repair', 'Needs Repair'),
    ])
    pickup_date = models.DateField()
    pincode = models.CharField(max_length=10)
    issue_description = models.TextField(blank=True, null=True)
    pickup_address = models.TextField()
    phone_images = models.FileField(upload_to="phone_images/", blank=True, null=True)
    expected_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.expected_price = self.calculate_expected_price()
        super().save(*args, **kwargs)

    def calculate_expected_price(self):
        base_price = 10000  # Example base price, you can adjust based on category
        condition_price_mapping = {
            'Like New': 0.9,
            'Good': 0.7,
            'Average': 0.5,
            'Needs Repair': 0.3,
        }
        price_factor = condition_price_mapping.get(self.phone_condition, 0.5)
        return base_price * price_factor
