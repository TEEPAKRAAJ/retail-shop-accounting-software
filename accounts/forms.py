from django import forms
import datetime
from django.contrib.auth.forms import UserCreationForm ,AuthenticationForm
from django.contrib.auth.models import User

PAYMENT_MODE_CHOICES = [
    ('GPay', 'GPay'),
    ('Cash', 'Cash'),
]

class StyledAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'class': 'w-full px-4 py-2 rounded border border-gray-300 focus:ring-2 focus:ring-blue-400 focus:outline-none bg-white'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'w-full px-4 py-2 rounded border border-gray-300 focus:ring-2 focus:ring-blue-400 focus:outline-none bg-white'
        })
    )


class StyledUserCreationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 rounded border border-gray-300 focus:ring-2 focus:ring-blue-400 focus:outline-none bg-white',
            'placeholder': 'Username'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 rounded border border-gray-300 focus:ring-2 focus:ring-blue-400 focus:outline-none bg-white',
            'placeholder': 'Password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 rounded border border-gray-300 focus:ring-2 focus:ring-blue-400 focus:outline-none bg-white',
            'placeholder': 'Confirm Password'
        })
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")


class SaleForm(forms.Form):
    gpay_amount = forms.DecimalField(
        label="GPay Amount",
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter GPay amount'})
    )
    cash_amount = forms.DecimalField(
        label="Cash Amount",
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter Cash amount'})
    )
    date = forms.DateField(
        label="Date",
        initial=datetime.date.today,
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'Select date'}),
        required=True
    )

class BillForm(forms.Form):
    restocking = forms.DecimalField(
        label="Restocking",
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter restocking amount'})
    )
    restocking_mode = forms.ChoiceField(
        label="Restocking Payment Mode",
        choices=PAYMENT_MODE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'placeholder': 'Select mode'})
    )
    rent = forms.DecimalField(
        label="Rent",
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter rent amount'})
    )
    rent_mode = forms.ChoiceField(
        label="Rent Payment Mode",
        choices=PAYMENT_MODE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'placeholder': 'Select mode'})
    )
    EB_bills = forms.DecimalField(
        label="EB Bills",
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter EB bills amount'})
    )
    EB_bills_mode = forms.ChoiceField(
        label="EB Bills Payment Mode",
        choices=PAYMENT_MODE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'placeholder': 'Select mode'})
    )
    wifi = forms.DecimalField(
        label="WiFi",
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter WiFi amount'})
    )
    wifi_mode = forms.ChoiceField(
        label="WiFi Payment Mode",
        choices=PAYMENT_MODE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'placeholder': 'Select mode'})
    )
    petrol = forms.DecimalField(
        label="Petrol",
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter petrol amount'})
    )
    petrol_mode = forms.ChoiceField(
        label="Petrol Payment Mode",
        choices=PAYMENT_MODE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'placeholder': 'Select mode'})
    )
    labor = forms.DecimalField(
        label="Labor",
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter labor amount'})
    )
    labor_mode = forms.ChoiceField(
        label="Labor Payment Mode",
        choices=PAYMENT_MODE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'placeholder': 'Select mode'})
    )
    other_category = forms.CharField(
        label="Other Category",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter other category'})
    )
    other_amount = forms.DecimalField(
        label="Other Amount",
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter other amount'})
    )
    other_mode = forms.ChoiceField(
        label="Other Payment Mode",
        choices=PAYMENT_MODE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'placeholder': 'Select mode'})
    )
    date = forms.DateField(
        label="Date",
        initial=datetime.date.today,
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'Select date'}),
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
    name = forms.CharField(
        label="Lender/Receiver Name",
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter name'})
    )
    is_lender = forms.ChoiceField(
        label="Type",
        choices=[('True', "Lender"), ('False', "Receiver")],
        required=True,
        widget=forms.Select(attrs={'placeholder': 'Select type'})
    )
    amount = forms.DecimalField(
        label="Amount",
        max_digits=12,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter amount'})
    )
    remarks = forms.CharField(
        label="Remarks",
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter Remarks'})
    )
    date = forms.DateField(
        label="Date",
        initial=datetime.date.today,
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'Select date'}),
        required=True
    )
    mode_of_payment = forms.ChoiceField(
        label="Mode of Payment",
        choices=[('GPay', 'GPay'), ('Cash', 'Cash')],
        required=True,
        widget=forms.Select(attrs={'placeholder': 'Select mode'})
    )
    