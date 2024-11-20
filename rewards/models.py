from django.db import models
from user.models import Users

from django.core.validators import MinValueValidator




class Product(models.Model):
    name=models.CharField(max_length=60, unique=True)
    coins=models.IntegerField()
    description=models.CharField(100)
    quantity=models.IntegerField(validators=[MinValueValidator(0)])
    color=models.CharField(max_length=20)
    image=models.ImageField(upload_to='products_image/',blank=True)
    is_listed=models.BooleanField(default=True)

    def __str__(self):
        return self.name
 

class Address(models.Model):
    user=models.ForeignKey(Users,on_delete=models.CASCADE)
    name=models.CharField(max_length=50)
    address=models.TextField()
    city=models.CharField(max_length=20)
    state=models.CharField(max_length=20)
    country=models.CharField(max_length=20)
    number=models.CharField(max_length=15)
    pincode=models.BigIntegerField()
    is_available=models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"'{self.name}'s address"


class Order(models.Model):
    STATUS_CHOICES = (
        ('Ordered', 'Ordered'),
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Canceled', 'Canceled'),
    )
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(Users,on_delete=models.SET_NULL, null=True, blank=True)
    address = models.ForeignKey(Address,on_delete=models.SET_NULL, null=True, blank=True)
    coin = models.CharField(max_length=10)
    order_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    expected_date = models.DateField(null=True)

    def __str__(self) -> str:
        return f"{self.user}'s Order {self.id}" 
    
