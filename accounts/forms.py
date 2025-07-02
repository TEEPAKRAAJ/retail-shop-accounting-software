from django import forms
import datetime

PAYMENT_MODE_CHOICES = [
    ('GPay', 'GPay'),
    ('Cash', 'Cash'),
]

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
    restocking_mode = forms.ChoiceField(label="Restocking Payment Mode", choices=PAYMENT_MODE_CHOICES, required=False)
    rent = forms.DecimalField(label="Rent", max_digits=10, decimal_places=2, required=False)
    rent_mode = forms.ChoiceField(label="Rent Payment Mode", choices=PAYMENT_MODE_CHOICES, required=False)
    EB_bills = forms.DecimalField(label="EB Bills", max_digits=10, decimal_places=2, required=False)
    EB_bills_mode = forms.ChoiceField(label="EB Bills Payment Mode", choices=PAYMENT_MODE_CHOICES, required=False)
    wifi = forms.DecimalField(label="WiFi", max_digits=10, decimal_places=2, required=False)
    wifi_mode = forms.ChoiceField(label="WiFi Payment Mode", choices=PAYMENT_MODE_CHOICES, required=False)
    petrol = forms.DecimalField(label="Petrol", max_digits=10, decimal_places=2, required=False)
    petrol_mode = forms.ChoiceField(label="Petrol Payment Mode", choices=PAYMENT_MODE_CHOICES, required=False)
    labor = forms.DecimalField(label="Labor", max_digits=10, decimal_places=2, required=False)
    labor_mode = forms.ChoiceField(label="Labor Payment Mode", choices=PAYMENT_MODE_CHOICES, required=False)
    other_category = forms.CharField(label="Other Category", max_length=100, required=False)
    other_amount = forms.DecimalField(label="Other Amount", max_digits=10, decimal_places=2, required=False)
    other_mode = forms.ChoiceField(label="Other Payment Mode", choices=PAYMENT_MODE_CHOICES, required=False)
    date = forms.DateField(
        label="Date",
        initial=datetime.date.today,
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        bill_fields = [
            ('restocking', 'restocking_mode'),
            ('rent', 'rent_mode'),
            ('EB_bills', 'EB_bills_mode'),
            ('wifi', 'wifi_mode'),
            ('petrol', 'petrol_mode'),
            ('labor', 'labor_mode'),
            ('other_amount', 'other_mode'),
        ]
        for amount_field, mode_field in bill_fields:
            amount = cleaned_data.get(amount_field)
            mode = cleaned_data.get(mode_field)
            if amount and not mode:
                self.add_error(mode_field, "This field is required if amount is entered.")
        return cleaned_data

class CreditForm(forms.Form):
    name = forms.CharField(label="Lender/Receiver Name", max_length=255, required=True)
    is_lender = forms.ChoiceField(
        label="Type",
        choices=[('True', "Lender"), ('False', "Receiver")],
        required=True
    )
    amount = forms.DecimalField(label="Amount", max_digits=12, decimal_places=2, required=True)
    remarks = forms.CharField(label="Remarks", max_length=255, required=True)
    mode_of_payment = forms.ChoiceField(
        label="Mode of Payment",
        choices=[('GPay', 'GPay'), ('Cash', 'Cash')],
        required=True
    )
    date = forms.DateField(
        label="Date",
        initial=datetime.date.today,
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    