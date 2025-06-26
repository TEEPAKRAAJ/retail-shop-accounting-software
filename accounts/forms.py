from django import forms

class SaleForm(forms.Form):
    gpay_amount = forms.DecimalField(label="GPay Amount", max_digits=10, decimal_places=2, required=False)
    cash_amount = forms.DecimalField(label="Cash Amount", max_digits=10, decimal_places=2, required=False)