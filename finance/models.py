from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal

# Predefined standard categories
INCOME_CATEGORIES = [
    ('Salary', 'Salary & Wages'),
    ('Freelance', 'Freelance & Consulting'),
    ('Investments', 'Investments & Dividends'),
    ('Business', 'Business Income'),
    ('Gifts', 'Gifts & Grants'),
    ('Rental', 'Rental Income'),
    ('Other Income', 'Other Income'),
]

EXPENSE_CATEGORIES = [
    ('Housing', 'Housing & Rent'),
    ('Groceries', 'Groceries & Supermarket'),
    ('Dining Out', 'Food & Dining Out'),
    ('Utilities', 'Utilities & Bills'),
    ('Transportation', 'Transportation & Fuel'),
    ('Entertainment', 'Entertainment & Recreation'),
    ('Healthcare', 'Healthcare & Medical'),
    ('Shopping', 'Shopping & Electronics'),
    ('Education', 'Education & Courses'),
    ('Personal Care', 'Personal Care & Fitness'),
    ('Travel', 'Travel & Vacation'),
    ('Subscriptions', 'Subscriptions & Services'),
    ('Other Expense', 'Other Expenses'),
]

ALL_CATEGORIES = INCOME_CATEGORIES + EXPENSE_CATEGORIES


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    title = models.CharField(max_length=200, help_text="e.g. Monthly Salary, Grocery Run, Electricity Bill")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='EXPENSE')
    category = models.CharField(max_length=50)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.transaction_type}: ${self.amount}"


class Budget(models.Model):
    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Monthly budget spending limit")
    month = models.IntegerField(choices=MONTH_CHOICES, default=timezone.now().month)
    year = models.IntegerField(default=timezone.now().year)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year', '-month', 'category']
        unique_together = ('user', 'category', 'month', 'year')

    def __str__(self):
        return f"{self.category} Budget ({self.get_month_display()} {self.year}): ${self.amount}"

    def get_spent_amount(self):
        """Calculates actual expense transactions in this category for the month and year."""
        total = Transaction.objects.filter(
            user=self.user,
            transaction_type='EXPENSE',
            category=self.category,
            date__year=self.year,
            date__month=self.month
        ).aggregate(total=Sum('amount'))['total']
        return total or Decimal('0.00')

    def get_remaining_amount(self):
        """Calculates remaining budget allowance."""
        return self.amount - self.get_spent_amount()

    def get_percentage_spent(self):
        """Percentage of budget spent."""
        if self.amount <= 0:
            return 0
        spent = self.get_spent_amount()
        pct = (spent / self.amount) * 100
        return round(float(pct), 1)

    def is_exceeded(self):
        """True if actual spending is strictly greater than budget."""
        return self.get_spent_amount() > self.amount

    def is_warning(self):
        """True if actual spending is 85% or more of budget, but not yet exceeded."""
        pct = self.get_percentage_spent()
        return 85 <= pct <= 100


class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savings_goals')
    name = models.CharField(max_length=200, help_text="e.g. Emergency Fund, New Car, Summer Vacation")
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    target_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['target_date', '-created_at']

    def __str__(self):
        return f"{self.name} - ${self.current_amount} of ${self.target_amount}"

    def get_percentage(self):
        if self.target_amount <= 0:
            return 0
        pct = (self.current_amount / self.target_amount) * 100
        return min(round(float(pct), 1), 100.0)

    def get_raw_percentage(self):
        if self.target_amount <= 0:
            return 0
        return round(float((self.current_amount / self.target_amount) * 100), 1)

    def get_remaining_amount(self):
        rem = self.target_amount - self.current_amount
        return max(Decimal('0.00'), rem)

    def is_completed(self):
        return self.current_amount >= self.target_amount
