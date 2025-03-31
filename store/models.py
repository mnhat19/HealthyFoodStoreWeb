from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.core.files.storage import default_storage

class Product(models.Model):
    CATEGORIES = [
        ('fresh', 'Fresh Products'),
        ('cooking', 'Cooking Products'),
        ('drinks', 'Drinks'),
        ('dishes', 'Dishes'),
        ('desserts', 'Desserts'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    ingredients = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORIES)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class HomePage(models.Model):
    bestsellers = models.ManyToManyField(Product, related_name='bestseller_products')
    background_image = models.ImageField(upload_to='homepage/')
    new_products = models.ManyToManyField(Product, related_name='new_products')

    def save(self, *args, **kwargs):
        """Xóa ảnh cũ khi cập nhật ảnh mới"""
        try:
            if self.pk:  # Kiểm tra nếu đối tượng đã tồn tại
                old_instance = HomePage.objects.get(pk=self.pk)
                if old_instance.background_image and old_instance.background_image.name != self.background_image.name:
                    if default_storage.exists(old_instance.background_image.name):
                        default_storage.delete(old_instance.background_image.name)
        except HomePage.DoesNotExist:
            pass  # Nếu không có ảnh cũ, bỏ qua

        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Home Page"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return self.user.username

class Payment(models.Model):
    name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50, blank=True)
    qr_code = models.ImageField(upload_to='payments/', blank=True)
    
    def __str__(self):
        return self.name

# class Order(models.Model):
#     STATUS_CHOICES = [
#         ('unpaid', 'Unpaid'),
#         ('paid', 'Paid'),
#     ]
    
#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')
#     created_at = models.DateTimeField(auto_now_add=True)
#     payment_method = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
#     def __str__(self):
#         return f"Order {self.id} - {self.customer.user.username}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('confirmed', 'Confirmed'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order {self.id} - {self.customer.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username
    
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)