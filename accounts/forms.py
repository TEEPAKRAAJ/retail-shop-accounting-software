from django import forms
import datetime

class SaleForm(forms.Form):
    gpay_amount = forms.DecimalField(label="GPay Amount", max_digits=10, decimal_places=2, required=False)
    cash_amount = forms.DecimalField(label="Cash Amount", max_digits=10, decimal_places=2, required=False)
    date = forms.DateField(
        label="Date",
        initial=datetime.date.today,
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )

class BillForm(forms.Form):
    restocking = forms.DecimalField(label="Restocking", max_digits=10, decimal_places=2, required=False)
    rent = forms.DecimalField(label="Rent", max_digits=10, decimal_places=2, required=False)
    EB_bills = forms.DecimalField(label="EB Bills", max_digits=10, decimal_places=2, required=False)
    wifi = forms.DecimalField(label="WiFi", max_digits=10, decimal_places=2, required=False)
    petrol = forms.DecimalField(label="Petrol", max_digits=10, decimal_places=2, required=False)
    labor = forms.DecimalField(label="Labor", max_digits=10, decimal_places=2, required=False)
    other_category = forms.CharField(label="Other Category", max_length=100, required=False)
    other_amount = forms.DecimalField(label="Other Amount", max_digits=10, decimal_places=2, required=False)
    date = forms.DateField(
        label="Date",
        initial=datetime.date.today,
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )