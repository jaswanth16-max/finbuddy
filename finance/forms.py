from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from decimal import Decimal
from .models import Transaction, Budget, SavingsGoal, EXPENSE_CATEGORIES, INCOME_CATEGORIES, ALL_CATEGORIES


class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'e.g. John'
    }))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'e.g. Doe'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'e.g. john.doe@example.com'
    }))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        self.fields['username'].help_text = "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        for field in self.fields:
            if 'password' in field:
                self.fields[field].widget.attrs.update({'class': 'form-control'})


class TransactionForm(forms.ModelForm):
    category = forms.ChoiceField(
        choices=[('', '-- Select Category --')] + ALL_CATEGORIES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_category'})
    )

    class Meta:
        model = Transaction
        fields = ['title', 'amount', 'transaction_type', 'category', 'date', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Salary, Grocery shopping, Electric bill'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'transaction_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_transaction_type'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes or receipt details...'
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount


class BudgetForm(forms.ModelForm):
    category = forms.ChoiceField(
        choices=[('', '-- Select Expense Category --')] + EXPENSE_CATEGORIES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Budget
        fields = ['category', 'amount', 'month', 'year']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'month': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '2020',
                'max': '2050'
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Monthly budget limit must be greater than zero.")
        return amount


class SavingsGoalForm(forms.ModelForm):
    class Meta:
        model = SavingsGoal
        fields = ['name', 'target_amount', 'current_amount', 'target_date', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Emergency Fund, New Car, Vacation'
            }),
            'target_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'current_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.00'
            }),
            'target_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Goal strategy, notes, or motivation...'
            }),
        }

    def clean_target_amount(self):
        target = self.cleaned_data.get('target_amount')
        if target is not None and target <= 0:
            raise forms.ValidationError("Target amount must be greater than zero.")
        return target

    def clean_current_amount(self):
        current = self.cleaned_data.get('current_amount')
        if current is not None and current < 0:
            raise forms.ValidationError("Current saved amount cannot be negative.")
        return current


class SavingsDepositForm(forms.Form):
    deposit_amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter amount to add',
            'step': '0.01',
            'min': '0.01'
        })
    )
