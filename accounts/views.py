from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Shop, Transaction
from .forms import SaleForm, BillForm
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.utils import timezone

def home(request):
    #messages.info(request, "Test message")
    return render(request, 'accounts/home.html')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data.get('username')
            user.save()
            print("User saved")
            login(request, user)
            print("User logged in")
            return redirect('home')
        else:
            print("Form invalid:", form.errors)
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def add_sale(request):
    try:
        shop = Shop.objects.get(owner=request.user)
    except Shop.DoesNotExist:
        messages.error(request, "You do not have a shop. Please contact admin.")
        return redirect('home')
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            gpay = form.cleaned_data.get('gpay_amount')
            cash = form.cleaned_data.get('cash_amount')
            date = form.cleaned_data.get('date')
            if gpay:
                Transaction.objects.create(
                    shop=shop, date=date, type='sale', category='GPay', amount=gpay
                )
            if cash:
                Transaction.objects.create(
                    shop=shop, date=date, type='sale', category='Cash', amount=cash
                )
            return redirect('add_sale')
    else:
        form = SaleForm()
    logs = Transaction.objects.filter(shop=shop).order_by('-date')
    return render(request, 'accounts/add_sale.html', {'form': form, 'logs': logs, 'now': timezone.now()})

@login_required
def add_bill(request):
    try:
        shop = Shop.objects.get(owner=request.user)
    except Shop.DoesNotExist:
        messages.error(request, "You do not have a shop. Please contact admin.")
        return redirect('home')
    if request.method == 'POST':
        form = BillForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data.get('date')
            bill_fields = [
                ('restocking', 'Restocking'),
                ('rent', 'Rent'),
                ('EB_bills', 'EB Bills'),
                ('wifi', 'WiFi'),
                ('petrol', 'Petrol'),
                ('labor', 'Labor'),
            ]
            for field, label in bill_fields:
                amount = form.cleaned_data.get(field)
                if amount:
                    Transaction.objects.create(
                        shop=shop, date=date, type='bill', category=label, amount=amount
                    )
            # Handle "other" category
            other_category = form.cleaned_data.get('other_category')
            other_amount = form.cleaned_data.get('other_amount')
            if other_category and other_amount:
                Transaction.objects.create(
                    shop=shop, date=date, type='bill', category=other_category, amount=other_amount
                )
            return redirect('add_bill')
    else:
        form = BillForm()
    logs = Transaction.objects.filter(shop=shop).order_by('-date')
    return render(request, 'accounts/add_bill.html', {'form': form, 'logs': logs, 'now': timezone.now()})

@require_POST
def logout_view(request):
    messages.success(request, "You have been logged out.")
    logout(request)
    return redirect('home')
