from django.db import models
from django.contrib.auth.models import User

class Shop(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=255)
    unique_id = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.shop_name

class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('sale', 'Sale'),
        ('bill', 'Bill'),
    ]
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    date = models.DateField()
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    category = models.CharField(max_length=100) 
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.shop.shop_name} - {self.type} - {self.category} - ₹{self.amount}"