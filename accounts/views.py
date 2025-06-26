from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Shop, Sale
from .forms import SaleForm
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
            today = timezone.now().date()
            if gpay:
                Sale.objects.create(shop=shop, date=today, method='gpay', amount=gpay)
            if cash:
                Sale.objects.create(shop=shop, date=today, method='cash', amount=cash)
            return redirect('add_sale')
    else:
        form = SaleForm()
    sales_log = Sale.objects.filter(shop=shop).order_by('-date')
    return render(request, 'accounts/add_sale.html', {'form': form, 'sales_log': sales_log, 'now': timezone.now()})


@login_required
def sale_list(request):
    shop = Shop.objects.get(owner=request.user)
    sales = Sale.objects.filter(shop=shop).order_by('-date')
    return render(request, 'account/sale_list.html', {'sales': sales})


@require_POST
def logout_view(request):
    messages.success(request, "You have been logged out.")
    logout(request)
    return redirect('home')
