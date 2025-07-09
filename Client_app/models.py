from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
  name=models.CharField(max_length=100,null=True)
  price=models.IntegerField(null=True)
  stock=models.IntegerField(null=True)
  product_image=models.ImageField(upload_to='media/',null=True)
  description = models.TextField(null=True, blank=True)
  categ= models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)
  def __str__(self):
    return self.name

class User_details(models.Model):
  name=models.CharField(max_length=30,null=True)
  Email_id=models.EmailField(max_length=50,null=True)
  Phone_number=models.CharField(max_length=15,null=True)
  password=models.CharField(max_length=20,null=True)
  confpassword=models.CharField(max_length=20,null=True)
  def __str__(self):
    return self.name


class Category(models.Model):
  name=models.CharField(max_length=50,null=True)
  description=models.TextField(null=True, blank=True)

  def __str__(self):
    return self.name

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

