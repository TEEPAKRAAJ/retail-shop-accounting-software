from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Shop, Transaction, CreditDue, CreditLog
from .forms import SaleForm, BillForm, CreditForm, StyledUserCreationForm, StyledAuthenticationForm
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.db.models import Sum
from django.http import JsonResponse, HttpResponse
import json
from datetime import datetime, timedelta
import calendar
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO


def home(request):
    #messages.info(request, "Test message")
    return render(request, 'accounts/home.html')

def login_view(request):
    if request.method == 'POST':
        form = StyledAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = StyledAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})
def signup_view(request):
    if request.method == 'POST':
        form = StyledUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data.get('username')
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = StyledUserCreationForm()
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
                    shop=shop, date=date, type='sale', category='Sale', amount=gpay, mode_of_payment='GPay'
                )
                shop.holding_gpay += gpay
            if cash:
                Transaction.objects.create(
                    shop=shop, date=date, type='sale', category='Sale', amount=cash, mode_of_payment='Cash'
                )
                shop.holding_cash += cash
            shop.save()
            messages.success(request, "Sale entry added successfully.")
            return redirect('add_sale')
    else:
        form = SaleForm()
    
    # Get all transactions
    logs = Transaction.objects.filter(shop=shop).order_by('-date')
    total_count = logs.count()
    
    return render(request, 'accounts/add_sale.html', {
        'form': form,
        'logs': logs,
        'total_count': total_count,
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
    
    # Get all transactions
    logs = Transaction.objects.filter(shop=shop).order_by('-date')
    total_count = logs.count()
    
    return render(request, 'accounts/add_bill.html', {
        'form': form,
        'logs': logs,
        'total_count': total_count,
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
                date=timezone.make_aware(datetime.combine(date, datetime.min.time())),
                mode_of_payment=mode_of_payment
            )
            messages.success(request, "Credit entry added/updated successfully.")
            return redirect('add_credit')
    else:
        form = CreditForm()
    
    credits = CreditDue.objects.filter(shop=shop)
    # Get latest 20 credit logs
    logs = CreditLog.objects.filter(credit__shop=shop).order_by('-date')[:20]
    total_count = CreditLog.objects.filter(credit__shop=shop).count()
    
    return render(request, 'accounts/add_credit.html', {
        'form': form,
        'logs': logs,
        'credits': credits,
        'total_count': total_count,
        'shop': shop
    })

@login_required
def search(request):
    summary = None
    logs = None
    query = ''
    shop = None
    if hasattr(request.user, 'shop'):
        shop = request.user.shop
    else:
        try:
            shop = Shop.objects.get(owner=request.user)
        except Shop.DoesNotExist:
            shop = None

    if request.method == 'POST':
        query = request.POST.get('query', '').strip()
        if query:
            # Filter transactions for the given date (YYYY-MM-DD)
            logs = Transaction.objects.filter(shop__owner=request.user, date__icontains=query)
            # Summary: sum amounts grouped by category and mode_of_payment
            summary = (
                logs.values('category', 'mode_of_payment')
                .annotate(total_amount=Sum('amount'))
                .order_by('category', 'mode_of_payment')
            )
        else:
            messages.error(request, "Please enter a valid search term.")
    return render(request, 'accounts/search.html', {
        'summary': summary,
        'logs': logs,
        'query': query,
        'shop': shop,
    })

from django.utils import timezone

@login_required
def monthly_report(request):
    shop = Shop.objects.get(owner=request.user)
    summary = None
    logs = None
    month = ''
    year = ''
    chart_data = None
    
    if request.method == 'POST':
        month = request.POST.get('month', '').strip()
        year = request.POST.get('year', '').strip()
        if month and year:
            try:
                month = int(month)
                year = int(year)
                logs = Transaction.objects.filter(
                    shop=shop,
                    date__year=year,
                    date__month=month
                ).order_by('-date')
                summary = (
                    logs.values('category', 'mode_of_payment')
                    .annotate(total_amount=Sum('amount'))
                    .order_by('category', 'mode_of_payment')
                )
                
                # Generate chart data
                chart_data = generate_monthly_chart_data(shop, year, month)
                
            except ValueError:
                messages.error(request, "Invalid month or year.")
        else:
            messages.error(request, "Please enter both month and year.")
    
    return render(request, 'accounts/monthly_report.html', {
        'summary': summary,
        'logs': logs,
        'month': month,
        'year': year,
        'shop': shop,
        'chart_data': chart_data,
    })

@login_required
def monthly_report_pdf(request):
    """Separate endpoint for PDF download"""
    shop = Shop.objects.get(owner=request.user)
    month = request.GET.get('month', '').strip()
    year = request.GET.get('year', '').strip()
    
    if month and year:
        try:
            month = int(month)
            year = int(year)
            logs = Transaction.objects.filter(
                shop=shop,
                date__year=year,
                date__month=month
            ).order_by('-date')
            summary = (
                logs.values('category', 'mode_of_payment')
                .annotate(total_amount=Sum('amount'))
                .order_by('category', 'mode_of_payment')
            )
            chart_data = generate_monthly_chart_data(shop, year, month)
            
            return generate_monthly_pdf(shop, logs, summary, chart_data, month, year)
        except ValueError:
            return JsonResponse({'error': 'Invalid month or year'})
    
    return JsonResponse({'error': 'Month and year required'})

@login_required
def yearly_report(request):
    shop = Shop.objects.get(owner=request.user)
    summary = None
    logs = None
    year = ''
    chart_data = None
    
    if request.method == 'POST':
        year = request.POST.get('year', '').strip()
        if year:
            try:
                year = int(year)
                logs = Transaction.objects.filter(
                    shop=shop,
                    date__year=year
                ).order_by('-date')
                summary = (
                    logs.values('category', 'mode_of_payment')
                    .annotate(total_amount=Sum('amount'))
                    .order_by('category', 'mode_of_payment')
                )
                
                # Generate chart data
                chart_data = generate_yearly_chart_data(shop, year)
                
            except ValueError:
                messages.error(request, "Invalid year.")
        else:
            messages.error(request, "Please enter a year.")
    
    return render(request, 'accounts/yearly_report.html', {
        'summary': summary,
        'logs': logs,
        'year': year,
        'shop': shop,
        'chart_data': chart_data,
    })

@login_required
def yearly_report_pdf(request):
    """Separate endpoint for PDF download"""
    shop = Shop.objects.get(owner=request.user)
    year = request.GET.get('year', '').strip()
    
    if year:
        try:
            year = int(year)
            logs = Transaction.objects.filter(
                shop=shop,
                date__year=year
            ).order_by('-date')
            summary = (
                logs.values('category', 'mode_of_payment')
                .annotate(total_amount=Sum('amount'))
                .order_by('category', 'mode_of_payment')
            )
            chart_data = generate_yearly_chart_data(shop, year)
            
            return generate_yearly_pdf(shop, logs, summary, chart_data, year)
        except ValueError:
            return JsonResponse({'error': 'Invalid year'})
    
    return JsonResponse({'error': 'Year required'})

def generate_monthly_chart_data(shop, year, month):
    """Generate chart data for monthly report"""
    # Get all days in the month
    num_days = calendar.monthrange(year, month)[1]
    days = list(range(1, num_days + 1))
    
    # Initialize data structures
    sales_gpay = []
    sales_cash = []
    bills_gpay = []
    bills_cash = []
    
    for day in days:
        date = datetime(year, month, day).date()
        
        # Sales data
        gpay_sales = Transaction.objects.filter(
            shop=shop, date=date, type='sale', mode_of_payment='GPay'
        ).aggregate(total=Sum('amount'))['total'] or 0
        cash_sales = Transaction.objects.filter(
            shop=shop, date=date, type='sale', mode_of_payment='Cash'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Bills data
        gpay_bills = Transaction.objects.filter(
            shop=shop, date=date, type='bill', mode_of_payment='GPay'
        ).aggregate(total=Sum('amount'))['total'] or 0
        cash_bills = Transaction.objects.filter(
            shop=shop, date=date, type='bill', mode_of_payment='Cash'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        sales_gpay.append(float(gpay_sales))
        sales_cash.append(float(cash_sales))
        bills_gpay.append(float(gpay_bills))
        bills_cash.append(float(cash_bills))
    
    return {
        'days': days,
        'sales_gpay': sales_gpay,
        'sales_cash': sales_cash,
        'bills_gpay': bills_gpay,
        'bills_cash': bills_cash,
        'month_name': calendar.month_name[month],
        'year': year
    }

def generate_yearly_chart_data(shop, year):
    """Generate chart data for yearly report"""
    months = list(range(1, 13))
    
    # Initialize data structures
    sales_gpay = []
    sales_cash = []
    bills_gpay = []
    bills_cash = []
    
    for month in months:
        # Sales data
        gpay_sales = Transaction.objects.filter(
            shop=shop, date__year=year, date__month=month, 
            type='sale', mode_of_payment='GPay'
        ).aggregate(total=Sum('amount'))['total'] or 0
        cash_sales = Transaction.objects.filter(
            shop=shop, date__year=year, date__month=month, 
            type='sale', mode_of_payment='Cash'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Bills data
        gpay_bills = Transaction.objects.filter(
            shop=shop, date__year=year, date__month=month, 
            type='bill', mode_of_payment='GPay'
        ).aggregate(total=Sum('amount'))['total'] or 0
        cash_bills = Transaction.objects.filter(
            shop=shop, date__year=year, date__month=month, 
            type='bill', mode_of_payment='Cash'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        sales_gpay.append(float(gpay_sales))
        sales_cash.append(float(cash_sales))
        bills_gpay.append(float(gpay_bills))
        bills_cash.append(float(cash_bills))
    
    return {
        'months': [calendar.month_abbr[m] for m in months],
        'sales_gpay': sales_gpay,
        'sales_cash': sales_cash,
        'bills_gpay': bills_gpay,
        'bills_cash': bills_cash,
        'year': year
    }

def generate_monthly_pdf(shop, logs, summary, chart_data, month, year):
    """Generate a professional monthly PDF report with charts"""
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.linecharts import HorizontalLineChart
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.legends import Legend
    from reportlab.graphics import renderPDF
    from io import BytesIO
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')
    
    # Create the PDF document
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # Styles with proper font encoding
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1,  # Center alignment
        textColor=colors.HexColor('#1e3a8a'),
        fontName='Helvetica-Bold'
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#374151'),
        fontName='Helvetica-Bold'
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName='Helvetica'
    )
    
    # Header
    story.append(Paragraph(f"Monthly Financial Report", title_style))
    story.append(Paragraph(f"Period: {month}/{year}", normal_style))
    story.append(Paragraph(f"Shop: {shop.shop_name}", normal_style))
    story.append(Spacer(1, 20))
    
    # Holdings Summary
    story.append(Paragraph("Holdings Summary", heading_style))
    holdings_data = [
        ['Account', 'Amount (Rs.)'],
        ['GPay Holding', f"Rs. {shop.holding_gpay}"],
        ['Cash Holding', f"Rs. {shop.holding_cash}"],
        ['Credit/Loan', f"Rs. {shop.credit}"],
        ['Total', f"Rs. {shop.holding_gpay + shop.holding_cash}"]
    ]
    holdings_table = Table(holdings_data, colWidths=[2*inch, 1.5*inch])
    holdings_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
    ]))
    story.append(holdings_table)
    story.append(Spacer(1, 20))
    
    # Transaction Summary
    if summary:
        story.append(Paragraph("Transaction Summary", heading_style))
        summary_data = [['Category', 'Payment Mode', 'Amount (Rs.)']]
        for row in summary:
            summary_data.append([
                row['category'].title(),
                row['mode_of_payment'].title(),
                f"Rs. {row['total_amount']}"
            ])
        summary_table = Table(summary_data, colWidths=[1.5*inch, 1.5*inch, 1*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0fdf4')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bbf7d0')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))
    
    # Charts Section
    if chart_data:
        story.append(Paragraph("Financial Analysis Charts", heading_style))
        
        # Create charts using matplotlib
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Sales Chart
        days = chart_data['days']
        sales_gpay = chart_data['sales_gpay']
        sales_cash = chart_data['sales_cash']
        
        ax1.plot(days, sales_gpay, 'o-', color='#3b82f6', linewidth=2, label='GPay Sales')
        ax1.plot(days, sales_cash, 's-', color='#10b981', linewidth=2, label='Cash Sales')
        ax1.set_title('Daily Sales Trend', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Amount (Rs.)', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Bills Chart
        bills_gpay = chart_data['bills_gpay']
        bills_cash = chart_data['bills_cash']
        
        ax2.plot(days, bills_gpay, 'o-', color='#ef4444', linewidth=2, label='GPay Bills')
        ax2.plot(days, bills_cash, 's-', color='#f59e0b', linewidth=2, label='Cash Bills')
        ax2.set_title('Daily Bills Trend', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Day', fontsize=12)
        ax2.set_ylabel('Amount (Rs.)', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save chart to buffer
        chart_buffer = BytesIO()
        plt.savefig(chart_buffer, format='png', dpi=300, bbox_inches='tight')
        chart_buffer.seek(0)
        plt.close()
        
        # Add chart to PDF
        chart_image = Image(chart_buffer, width=7*inch, height=5*inch)
        story.append(chart_image)
        story.append(Spacer(1, 20))
    
    # Transaction Details
    if logs:
        story.append(Paragraph("Transaction Details", heading_style))
        transaction_data = [['Date', 'Type', 'Category', 'Payment Mode', 'Amount (Rs.)']]
        for log in logs[:50]:  # Limit to first 50 transactions
            transaction_data.append([
                log.date.strftime('%d-%m-%Y'),
                log.type.title(),
                log.category.title() if log.category else '-',
                log.mode_of_payment.title(),
                f"Rs. {log.amount}"
            ])
        transaction_table = Table(transaction_data, colWidths=[1*inch, 0.8*inch, 1.2*inch, 1*inch, 1*inch])
        transaction_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#faf5ff')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ddd6fe')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ALIGN', (4, 1), (-1, -1), 'RIGHT'),
        ]))
        story.append(transaction_table)
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph("Generated on: " + timezone.now().strftime('%d-%m-%Y %H:%M:%S'), normal_style))
    story.append(Paragraph("This is an automated financial report generated by the Shop Management System.", normal_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    # Create response
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="monthly_report_{year}_{month:02d}.pdf"'
    return response

def generate_yearly_pdf(shop, logs, summary, chart_data, year):
    """Generate a professional yearly PDF report with charts"""
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.linecharts import HorizontalLineChart
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.legends import Legend
    from reportlab.graphics import renderPDF
    from io import BytesIO
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')
    
    # Create the PDF document
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # Styles with proper font encoding
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1,  # Center alignment
        textColor=colors.HexColor('#1e3a8a'),
        fontName='Helvetica-Bold'
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#374151'),
        fontName='Helvetica-Bold'
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName='Helvetica'
    )
    
    # Header
    story.append(Paragraph(f"Yearly Financial Report", title_style))
    story.append(Paragraph(f"Year: {year}", normal_style))
    story.append(Paragraph(f"Shop: {shop.shop_name}", normal_style))
    story.append(Spacer(1, 20))
    
    # Holdings Summary
    story.append(Paragraph("Holdings Summary", heading_style))
    holdings_data = [
        ['Account', 'Amount (Rs.)'],
        ['GPay Holding', f"Rs. {shop.holding_gpay}"],
        ['Cash Holding', f"Rs. {shop.holding_cash}"],
        ['Credit/Loan', f"Rs. {shop.credit}"],
        ['Total', f"Rs. {shop.holding_gpay + shop.holding_cash}"]
    ]
    holdings_table = Table(holdings_data, colWidths=[2*inch, 1.5*inch])
    holdings_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
    ]))
    story.append(holdings_table)
    story.append(Spacer(1, 20))
    
    # Transaction Summary
    if summary:
        story.append(Paragraph("Transaction Summary", heading_style))
        summary_data = [['Category', 'Payment Mode', 'Amount (Rs.)']]
        for row in summary:
            summary_data.append([
                row['category'].title(),
                row['mode_of_payment'].title(),
                f"Rs. {row['total_amount']}"
            ])
        summary_table = Table(summary_data, colWidths=[1.5*inch, 1.5*inch, 1*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0fdf4')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bbf7d0')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))
    
    # Charts Section
    if chart_data:
        story.append(Paragraph("Financial Analysis Charts", heading_style))
        
        # Create charts using matplotlib
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Sales Chart
        months = chart_data['months']
        sales_gpay = chart_data['sales_gpay']
        sales_cash = chart_data['sales_cash']
        
        ax1.plot(months, sales_gpay, 'o-', color='#3b82f6', linewidth=2, label='GPay Sales')
        ax1.plot(months, sales_cash, 's-', color='#10b981', linewidth=2, label='Cash Sales')
        ax1.set_title('Monthly Sales Trend', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Amount (Rs.)', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Bills Chart
        bills_gpay = chart_data['bills_gpay']
        bills_cash = chart_data['bills_cash']
        
        ax2.plot(months, bills_gpay, 'o-', color='#ef4444', linewidth=2, label='GPay Bills')
        ax2.plot(months, bills_cash, 's-', color='#f59e0b', linewidth=2, label='Cash Bills')
        ax2.set_title('Monthly Bills Trend', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Month', fontsize=12)
        ax2.set_ylabel('Amount (Rs.)', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save chart to buffer
        chart_buffer = BytesIO()
        plt.savefig(chart_buffer, format='png', dpi=300, bbox_inches='tight')
        chart_buffer.seek(0)
        plt.close()
        
        # Add chart to PDF
        chart_image = Image(chart_buffer, width=7*inch, height=5*inch)
        story.append(chart_image)
        story.append(Spacer(1, 20))
    
    # Transaction Details
    if logs:
        story.append(Paragraph("Transaction Details", heading_style))
        transaction_data = [['Date', 'Type', 'Category', 'Payment Mode', 'Amount (Rs.)']]
        for log in logs[:50]:  # Limit to first 50 transactions
            transaction_data.append([
                log.date.strftime('%d-%m-%Y'),
                log.type.title(),
                log.category.title() if log.category else '-',
                log.mode_of_payment.title(),
                f"Rs. {log.amount}"
            ])
        transaction_table = Table(transaction_data, colWidths=[1*inch, 0.8*inch, 1.2*inch, 1*inch, 1*inch])
        transaction_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#faf5ff')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ddd6fe')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ALIGN', (4, 1), (-1, -1), 'RIGHT'),
        ]))
        story.append(transaction_table)
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph("Generated on: " + timezone.now().strftime('%d-%m-%Y %H:%M:%S'), normal_style))
    story.append(Paragraph("This is an automated financial report generated by the Shop Management System.", normal_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    # Create response
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="yearly_report_{year}.pdf"'
    return response

@require_POST
def logout_view(request):
    messages.success(request, "You have been logged out.")
    logout(request)
    return redirect('home')

@login_required
@require_POST
def delete_transaction(request, transaction_id):
    """Delete a transaction and reverse its effects on shop holdings"""
    try:
        shop = Shop.objects.get(owner=request.user)
        transaction = get_object_or_404(Transaction, id=transaction_id, shop=shop)
        
        # Reverse the transaction effects
        if transaction.type == 'sale':
            if transaction.mode_of_payment == 'GPay':
                shop.holding_gpay -= transaction.amount
            elif transaction.mode_of_payment == 'Cash':
                shop.holding_cash -= transaction.amount
        elif transaction.type == 'bill':
            if transaction.mode_of_payment == 'GPay':
                shop.holding_gpay += transaction.amount
            elif transaction.mode_of_payment == 'Cash':
                shop.holding_cash += transaction.amount
        
        shop.save()
        transaction.delete()
        
        return JsonResponse({'success': True, 'message': 'Transaction deleted successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_POST
def delete_credit_log(request, log_id):
    """Delete a credit log and reverse its effects"""
    try:
        shop = Shop.objects.get(owner=request.user)
        credit_log = get_object_or_404(CreditLog, id=log_id, credit__shop=shop)
        credit = credit_log.credit
        
        # Reverse the credit log effects
        if credit_log.is_lender:
            credit.balance += credit_log.amount
            if credit_log.mode_of_payment == 'GPay':
                shop.holding_gpay += credit_log.amount
            elif credit_log.mode_of_payment == 'Cash':
                shop.holding_cash += credit_log.amount
        else:
            credit.balance -= credit_log.amount
            if credit_log.mode_of_payment == 'GPay':
                shop.holding_gpay -= credit_log.amount
            elif credit_log.mode_of_payment == 'Cash':
                shop.holding_cash -= credit_log.amount
        
        # Update credit repaid status
        if credit.balance == 0:
            credit.repaid = True
            credit.end_date = None
        else:
            credit.repaid = False
            credit.end_date = None
        
        credit.save()
        
        # Update shop credit total
        shop.credit = CreditDue.objects.filter(shop=shop, repaid=False).aggregate(total=Sum('balance'))['total'] or 0
        shop.save()
        
        credit_log.delete()
        
        return JsonResponse({'success': True, 'message': 'Credit log deleted successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
def load_more_transactions(request):
    """Load more transactions via AJAX - Now returns all transactions"""
    try:
        shop = Shop.objects.get(owner=request.user)
        transactions = Transaction.objects.filter(shop=shop).order_by('-date')
        
        html = ''
        for transaction in transactions:
            # Determine color based on transaction type
            amount_color = 'text-green-700 dark:text-green-400' if transaction.type == 'sale' else 'text-red-700 dark:text-red-400'
            category_span = ''
            if transaction.type == 'bill' and transaction.category:
                category_span = f'<span class="inline-block px-2 py-0.5 rounded bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 font-semibold capitalize">{transaction.category}</span>'
            
            html += f'''
            <div id="transaction-{transaction.id}" class="log-item bg-gradient-to-r from-gray-100 to-gray-100 dark:from-gray-700 dark:to-gray-800 rounded-xl p-4 mb-3 shadow transition hover:scale-[1.01] hover:shadow-lg relative">
                <div class="flex justify-between items-center">
                    <div class="flex flex-wrap items-center gap-2 text-xs text-gray-500 dark:text-gray-400 mb-1">
                        <span class="inline-block px-2 py-0.5 rounded bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 font-semibold">
                            {transaction.date.strftime('%d-%m-%Y')}
                        </span>
                        <span class="inline-block px-2 py-0.5 rounded bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-semibold capitalize">
                            {transaction.type}
                        </span>
                        <span class="inline-block px-2 py-0.5 rounded bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 font-semibold capitalize">
                            {transaction.mode_of_payment}
                        </span>
                        {category_span}
                    </div>
                    <div class="flex items-center gap-2">
                        <div class="font-bold text-xl {amount_color}">
                            ₹{transaction.amount}
                        </div>
                        <button onclick="deleteTransaction({transaction.id})" 
                                class="delete-btn bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded-lg text-sm font-medium transition-all duration-200">
                            Delete
                        </button>
                    </div>
                </div>
            </div>
            '''
        
        return JsonResponse({
            'html': html,
            'has_more': False  # No more pagination needed
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})
