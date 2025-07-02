from django.contrib import admin
from .models import Shop, Transaction, CreditDue, CreditLog

admin.site.register(Shop)
admin.site.register(Transaction)
admin.site.register(CreditDue)
admin.site.register(CreditLog)