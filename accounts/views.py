from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Shop, Transaction, CreditDue, CreditLog
from .forms import SaleForm, BillForm, CreditForm
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
                    shop=shop, date=date, type='sale', category='GPay', amount=gpay, mode_of_payment='GPay'
                )
                shop.holding_gpay += gpay
            if cash:
                Transaction.objects.create(
                    shop=shop, date=date, type='sale', category='Cash', amount=cash, mode_of_payment='Cash'
                )
                shop.holding_cash += cash
            shop.save()
            messages.success(request, "Sale entry added successfully.")
            return redirect('add_sale')
    else:
        form = SaleForm()
    logs = Transaction.objects.filter(shop=shop).order_by('-date')
    return render(request, 'accounts/add_sale.html', {
        'form': form,
        'logs': logs,
        'now': timezone.now(),
        'shop': shop,
    })

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
                ('restocking', 'restocking_mode', 'Restocking'),
                ('rent', 'rent_mode', 'Rent'),
                ('EB_bills', 'EB_bills_mode', 'EB Bills'),
                ('wifi', 'wifi_mode', 'WiFi'),
                ('petrol', 'petrol_mode', 'Petrol'),
                ('labor', 'labor_mode', 'Labor'),
                ('other_amount', 'other_mode', 'Other'),
            ]
            updated = False
            for amount_field, mode_field, label in bill_fields:
                amount = form.cleaned_data.get(amount_field)
                mode = form.cleaned_data.get(mode_field)
                if amount is not None and amount != '':
                    if not mode:
                        messages.error(request, f"Please select mode of payment for {label}.")
                        return render(request, 'accounts/add_bill.html', {
                            'form': form,
                            'logs': Transaction.objects.filter(shop=shop).order_by('-date'),
                            'now': timezone.now(),
                            'shop': shop
                        })
                    Transaction.objects.create(
                        shop=shop, date=date, type='bill', category=label, amount=amount, mode_of_payment=mode
                    )
                    if mode == 'GPay':
                        shop.holding_gpay -= amount
                    elif mode == 'Cash':
                        shop.holding_cash -= amount
                    updated = True
            if updated:
                shop.save()
                messages.success(request, "Bill entry added/updated successfully.")
            return redirect('add_bill')
    else:
        form = BillForm()
    logs = Transaction.objects.filter(shop=shop).order_by('-date')
    return render(request, 'accounts/add_bill.html', {
        'form': form,
        'logs': logs,
        'now': timezone.now(),
        'shop': shop
    })
from django.utils import timezone

@login_required
def add_credit(request):
    try:
        shop = Shop.objects.get(owner=request.user)
    except Shop.DoesNotExist:
        messages.error(request, "You do not have a shop. Please contact admin.")
        return redirect('home')
    if request.method == 'POST':
        form = CreditForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            is_lender = form.cleaned_data['is_lender'] == 'True'
            amount = form.cleaned_data['amount']
            remarks = form.cleaned_data['remarks']
            date = form.cleaned_data['date']
            mode_of_payment = form.cleaned_data['mode_of_payment']

            # Only one Credit per (shop, name)
            credit, created = CreditDue.objects.get_or_create(
                shop=shop,
                name=name,
                defaults={
                    'balance': 0,
                    'start_date': date  # Use form date for new records
                }
            )

            # Lending: subtract (negative), Receiving: add (positive)
            if is_lender:
                credit.balance -= amount
                if mode_of_payment == 'GPay':
                    shop.holding_gpay -= amount
                elif mode_of_payment == 'Cash':
                    shop.holding_cash -= amount
            else:
                credit.balance += amount
                if mode_of_payment == 'GPay':
                    shop.holding_gpay += amount
                elif mode_of_payment == 'Cash':
                    shop.holding_cash += amount

            # If repaid, set end_date from form date
            if credit.balance == 0:
                credit.repaid = True
                credit.end_date = date  # Use form date
            else:
                credit.repaid = False
                credit.end_date = None

            credit.save()

            # Update shop.credit to sum of all non-repaid credits
            from django.db.models import Sum
            shop.credit = CreditDue.objects.filter(shop=shop, repaid=False).aggregate(total=Sum('balance'))['total'] or 0
            shop.save()

            # Add log: always positive amount, store is_lender, use form date
            CreditLog.objects.create(
                credit=credit,
                is_lender=is_lender,
                amount=amount,
                remarks=remarks,
                date=date
            )
            messages.success(request, "Credit entry added/updated successfully.")
            return redirect('add_credit')
    else:
        form = CreditForm()
    credits = CreditDue.objects.filter(shop=shop)
    logs = CreditLog.objects.filter(credit__shop=shop).order_by('-date')
    return render(request, 'accounts/add_credit.html', {
        'form': form,
        'logs': logs,
        'credits': credits,
        'shop': shop
    })

@require_POST
def logout_view(request):
    messages.success(request, "You have been logged out.")
    logout(request)
    return redirect('home')
