from django.contrib import admin
from .models import Transaction, Budget, SavingsGoal


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'amount', 'transaction_type', 'category', 'date')
    list_filter = ('transaction_type', 'category', 'date', 'user')
    search_fields = ('title', 'description', 'user__username')
    ordering = ('-date', '-created_at')


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('category', 'user', 'amount', 'month', 'year')
    list_filter = ('month', 'year', 'category', 'user')
    search_fields = ('category', 'user__username')


@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'current_amount', 'target_amount', 'target_date')
    list_filter = ('target_date', 'user')
    search_fields = ('name', 'description', 'user__username')
