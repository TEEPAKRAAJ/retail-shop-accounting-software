from django.db import models
from django.contrib.auth.models import User

class Shop(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=255)
    unique_id = models.CharField(max_length=10, unique=True)
    holding_gpay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    holding_cash = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.shop_name

class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('sale', 'Sale'),
        ('bill', 'Bill'),
    ]
    PAYMENT_MODE_CHOICES = [
        ('GPay', 'GPay'),
        ('Cash', 'Cash'),
    ]
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    date = models.DateField()
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # <-- ADD THIS LINE
    mode_of_payment = models.CharField(max_length=10, choices=PAYMENT_MODE_CHOICES)

    def __str__(self):
        return f"{self.shop.shop_name} - {self.type} - {self.category} - ₹{self.amount} ({self.mode_of_payment})"
    
class CreditDue(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='credit_dues')
    name = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    repaid = models.BooleanField(default=False)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        unique_together = ('shop', 'name')

    def __str__(self):
        role = "Lender" if self.balance < 0 else "Receiver"
        return f"{self.name} ({role}) - ₹{self.balance} {'[REPAID]' if self.repaid else ''}"

class CreditLog(models.Model):
    credit = models.ForeignKey(CreditDue, on_delete=models.CASCADE, related_name='logs')
    is_lender = models.BooleanField()  # True if lender, False if receiver
    date = models.DateTimeField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    mode_of_payment = models.CharField(max_length=10, choices=[('GPay', 'GPay'), ('Cash', 'Cash')], default='Cash')

    def __str__(self):
        role = "Lender" if self.is_lender else "Receiver"
        return f"{self.credit.name} ({role}) | {self.amount} on {self.date.strftime('%Y-%m-%d %H:%M')} ({self.mode_of_payment})"