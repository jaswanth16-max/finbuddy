import json
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone

from .models import Transaction, Budget, SavingsGoal, EXPENSE_CATEGORIES, INCOME_CATEGORIES
from .forms import UserRegisterForm, TransactionForm, BudgetForm, SavingsGoalForm, SavingsDepositForm


# ==========================================
# PUBLIC PAGES
# ==========================================

def home(request):
    """Modern landing page with hero, features, and benefits."""
    if request.user.is_authenticated:
        # User is already signed in; could go to landing with quick-access banner
        pass
    return render(request, 'home.html')


def about(request):
    """About page introducing FinBuddy's mission and financial principles."""
    return render(request, 'about.html')


# ==========================================
# AUTHENTICATION VIEWS
# ==========================================

def register_view(request):
    """Register new user, log them in automatically, and redirect to dashboard."""
    if request.user.is_authenticated:
        return redirect('finance:dashboard')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to FinBuddy, {user.first_name or user.username}! Your financial journey begins now.")
            return redirect('finance:dashboard')
        else:
            messages.error(request, "Please correct the errors below to register.")
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """Secure user login."""
    if request.user.is_authenticated:
        return redirect('finance:dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next') or 'finance:dashboard'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    """Secure user logout."""
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out securely. See you soon!")
    return redirect('finance:home')


# ==========================================
# DASHBOARD
# ==========================================

@login_required
def dashboard(request):
    """Main authenticated financial dashboard with metrics and Chart.js data."""
    user = request.user
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year

    # 1. Total Metrics (All-time)
    income_agg = Transaction.objects.filter(user=user, transaction_type='INCOME').aggregate(Sum('amount'))
    total_income = income_agg['amount__sum'] or Decimal('0.00')

    expense_agg = Transaction.objects.filter(user=user, transaction_type='EXPENSE').aggregate(Sum('amount'))
    total_expenses = expense_agg['amount__sum'] or Decimal('0.00')

    current_balance = total_income - total_expenses

    # 2. Monthly Budget Remaining (Current Month)
    current_month_budgets = Budget.objects.filter(user=user, month=current_month, year=current_year)
    total_monthly_budget = current_month_budgets.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    current_month_expenses = Transaction.objects.filter(
        user=user,
        transaction_type='EXPENSE',
        date__year=current_year,
        date__month=current_month
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    if total_monthly_budget > 0:
        monthly_budget_remaining = total_monthly_budget - current_month_expenses
    else:
        monthly_budget_remaining = Decimal('0.00')

    # 3. Recent Transactions (last 6)
    recent_transactions = Transaction.objects.filter(user=user)[:6]

    # 4. Active Budgets Preview (with attached computed properties)
    budget_previews = []
    for b in current_month_budgets[:4]:
        spent = b.get_spent_amount()
        pct = b.get_percentage_spent()
        budget_previews.append({
            'budget': b,
            'spent': spent,
            'remaining': b.get_remaining_amount(),
            'percentage': pct,
            'is_exceeded': b.is_exceeded(),
            'is_warning': b.is_warning(),
        })

    # 5. Savings Goals Preview (top 3)
    savings_goals = SavingsGoal.objects.filter(user=user)[:3]

    # 6. Chart.js Data Preparation
    # 6A: Income vs Expense (Doughnut)
    inc_exp_labels = ['Total Income', 'Total Expenses']
    inc_exp_data = [float(total_income), float(total_expenses)]

    # 6B: Category Breakdown for Expenses (Current Month & All-time fallback)
    cat_expenses = Transaction.objects.filter(
        user=user,
        transaction_type='EXPENSE'
    ).values('category').annotate(total=Sum('amount')).order_by('-total')[:6]

    cat_labels = [c['category'] for c in cat_expenses]
    cat_data = [float(c['total']) for c in cat_expenses]

    # 6C: Monthly spending & income trend (Past 6 months)
    months_labels = []
    monthly_income_data = []
    monthly_expense_data = []

    for i in range(5, -1, -1):
        target_month_date = today.replace(day=1) - timedelta(days=i * 30)
        m = target_month_date.month
        y = target_month_date.year
        month_name = target_month_date.strftime("%b %Y")
        months_labels.append(month_name)

        m_inc = Transaction.objects.filter(
            user=user,
            transaction_type='INCOME',
            date__year=y,
            date__month=m
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

        m_exp = Transaction.objects.filter(
            user=user,
            transaction_type='EXPENSE',
            date__year=y,
            date__month=m
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

        monthly_income_data.append(float(m_inc))
        monthly_expense_data.append(float(m_exp))

    quick_transaction_form = TransactionForm(initial={'date': today})

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'current_balance': current_balance,
        'total_monthly_budget': total_monthly_budget,
        'monthly_budget_remaining': monthly_budget_remaining,
        'current_month_expenses': current_month_expenses,
        'recent_transactions': recent_transactions,
        'budget_previews': budget_previews,
        'savings_goals': savings_goals,
        'quick_transaction_form': quick_transaction_form,
        'has_transactions': Transaction.objects.filter(user=user).exists(),
        # Chart JSON data
        'chart_inc_exp_labels': json.dumps(inc_exp_labels),
        'chart_inc_exp_data': json.dumps(inc_exp_data),
        'chart_cat_labels': json.dumps(cat_labels),
        'chart_cat_data': json.dumps(cat_data),
        'chart_months_labels': json.dumps(months_labels),
        'chart_monthly_income_data': json.dumps(monthly_income_data),
        'chart_monthly_expense_data': json.dumps(monthly_expense_data),
    }
    return render(request, 'finance/dashboard.html', context)


# ==========================================
# TRANSACTIONS MANAGEMENT
# ==========================================

@login_required
def transactions_list(request):
    """Transactions list view with filtering and search."""
    user = request.user
    queryset = Transaction.objects.filter(user=user)

    # Filter parameters
    search_query = request.GET.get('search', '').strip()
    trans_type = request.GET.get('type', '').strip().upper()
    category = request.GET.get('category', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    if trans_type in ['INCOME', 'EXPENSE']:
        queryset = queryset.filter(transaction_type=trans_type)

    if category:
        queryset = queryset.filter(category=category)

    if date_from:
        try:
            queryset = queryset.filter(date__gte=date_from)
        except Exception:
            pass

    if date_to:
        try:
            queryset = queryset.filter(date__lte=date_to)
        except Exception:
            pass

    # Dynamic totals for filtered results
    filtered_income = queryset.filter(transaction_type='INCOME').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    filtered_expense = queryset.filter(transaction_type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    filtered_net = filtered_income - filtered_expense

    # Categories list for filter dropdown
    user_categories = Transaction.objects.filter(user=user).values_list('category', flat=True).distinct()

    context = {
        'transactions': queryset,
        'search_query': search_query,
        'selected_type': trans_type,
        'selected_category': category,
        'date_from': date_from,
        'date_to': date_to,
        'user_categories': user_categories,
        'filtered_income': filtered_income,
        'filtered_expense': filtered_expense,
        'filtered_net': filtered_net,
        'quick_form': TransactionForm(initial={'date': timezone.now().date()}),
    }
    return render(request, 'finance/transactions.html', context)


@login_required
def transaction_create(request):
    """Add a new transaction."""
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, f"Transaction '{transaction.title}' added successfully!")
            next_url = request.POST.get('next') or request.GET.get('next') or 'finance:transactions_list'
            return redirect(next_url)
        else:
            messages.error(request, "Failed to add transaction. Please check form inputs.")
    else:
        form = TransactionForm(initial={'date': timezone.now().date()})
    return render(request, 'finance/transaction_form.html', {'form': form, 'title': 'Add New Transaction'})


@login_required
def transaction_update(request, pk):
    """Edit existing transaction."""
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, f"Transaction '{transaction.title}' updated successfully.")
            return redirect('finance:transactions_list')
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = TransactionForm(instance=transaction)
    return render(request, 'finance/transaction_form.html', {'form': form, 'title': 'Edit Transaction', 'transaction': transaction})


@login_required
def transaction_delete(request, pk):
    """Delete a transaction."""
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        title = transaction.title
        transaction.delete()
        messages.success(request, f"Transaction '{title}' deleted successfully.")
        return redirect('finance:transactions_list')
    return render(request, 'finance/transaction_confirm_delete.html', {'transaction': transaction})


# ==========================================
# BUDGET MANAGEMENT
# ==========================================

@login_required
def budget_list(request):
    """List budgets for selected month/year with spending trackers."""
    user = request.user
    today = timezone.now().date()

    selected_month = int(request.GET.get('month', today.month))
    selected_year = int(request.GET.get('year', today.year))

    budgets = Budget.objects.filter(user=user, month=selected_month, year=selected_year)

    total_budgeted = Decimal('0.00')
    total_spent = Decimal('0.00')
    exceeded_count = 0
    budget_cards = []

    for b in budgets:
        spent = b.get_spent_amount()
        rem = b.get_remaining_amount()
        pct = b.get_percentage_spent()
        exceeded = b.is_exceeded()
        warning = b.is_warning()

        total_budgeted += b.amount
        total_spent += spent
        if exceeded:
            exceeded_count += 1

        budget_cards.append({
            'budget': b,
            'spent': spent,
            'remaining': rem,
            'percentage': pct,
            'is_exceeded': exceeded,
            'is_warning': warning,
        })

    overall_remaining = total_budgeted - total_spent
    overall_pct = round((total_spent / total_budgeted * 100), 1) if total_budgeted > 0 else 0

    quick_form = BudgetForm(initial={'month': selected_month, 'year': selected_year})

    context = {
        'budget_cards': budget_cards,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'month_choices': Budget.MONTH_CHOICES,
        'year_choices': range(today.year - 2, today.year + 3),
        'total_budgeted': total_budgeted,
        'total_spent': total_spent,
        'overall_remaining': overall_remaining,
        'overall_pct': overall_pct,
        'exceeded_count': exceeded_count,
        'quick_form': quick_form,
    }
    return render(request, 'finance/budgets.html', context)


@login_required
def budget_create(request):
    """Create a new monthly budget."""
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            month = form.cleaned_data['month']
            year = form.cleaned_data['year']

            # Check if budget already exists
            existing = Budget.objects.filter(user=request.user, category=category, month=month, year=year).first()
            if existing:
                messages.warning(request, f"A budget for {category} already exists for this period. Updating amount instead.")
                existing.amount = form.cleaned_data['amount']
                existing.save()
            else:
                budget = form.save(commit=False)
                budget.user = request.user
                budget.save()
                messages.success(request, f"Budget for {budget.category} created successfully!")
            return redirect(f"/budgets/?month={month}&year={year}")
        else:
            messages.error(request, "Could not create budget. Please check input values.")
    else:
        form = BudgetForm(initial={'month': timezone.now().month, 'year': timezone.now().year})
    return render(request, 'finance/budget_form.html', {'form': form, 'title': 'Create Monthly Budget'})


@login_required
def budget_update(request, pk):
    """Edit existing budget."""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            messages.success(request, f"Budget for {budget.category} updated successfully.")
            return redirect(f"/budgets/?month={budget.month}&year={budget.year}")
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = BudgetForm(instance=budget)
    return render(request, 'finance/budget_form.html', {'form': form, 'title': 'Edit Budget', 'budget': budget})


@login_required
def budget_delete(request, pk):
    """Delete a budget."""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    month = budget.month
    year = budget.year
    if request.method == 'POST':
        cat = budget.category
        budget.delete()
        messages.success(request, f"Budget for {cat} deleted.")
        return redirect(f"/budgets/?month={month}&year={year}")
    return render(request, 'finance/budget_confirm_delete.html', {'budget': budget})


# ==========================================
# SAVINGS GOALS
# ==========================================

@login_required
def savings_goal_list(request):
    """List all savings goals with progress and deposit options."""
    user = request.user
    goals = SavingsGoal.objects.filter(user=user)

    total_target = goals.aggregate(Sum('target_amount'))['target_amount__sum'] or Decimal('0.00')
    total_saved = goals.aggregate(Sum('current_amount'))['current_amount__sum'] or Decimal('0.00')
    overall_progress = round(float((total_saved / total_target) * 100), 1) if total_target > 0 else 0
    completed_count = sum(1 for g in goals if g.is_completed())

    quick_form = SavingsGoalForm()
    deposit_form = SavingsDepositForm()

    context = {
        'goals': goals,
        'total_target': total_target,
        'total_saved': total_saved,
        'overall_progress': min(overall_progress, 100.0),
        'completed_count': completed_count,
        'quick_form': quick_form,
        'deposit_form': deposit_form,
    }
    return render(request, 'finance/savings_goals.html', context)


@login_required
def savings_goal_create(request):
    """Create a new savings goal."""
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, f"Savings goal '{goal.name}' created successfully!")
            return redirect('finance:savings_goal_list')
        else:
            messages.error(request, "Failed to create savings goal. Please check errors below.")
    else:
        form = SavingsGoalForm()
    return render(request, 'finance/savings_goal_form.html', {'form': form, 'title': 'Create Savings Goal'})


@login_required
def savings_goal_update(request, pk):
    """Edit existing savings goal."""
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, f"Savings goal '{goal.name}' updated successfully.")
            return redirect('finance:savings_goal_list')
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = SavingsGoalForm(instance=goal)
    return render(request, 'finance/savings_goal_form.html', {'form': form, 'title': 'Edit Savings Goal', 'goal': goal})


@login_required
def savings_goal_delete(request, pk):
    """Delete a savings goal."""
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        name = goal.name
        goal.delete()
        messages.success(request, f"Savings goal '{name}' deleted.")
        return redirect('finance:savings_goal_list')
    return render(request, 'finance/savings_goal_confirm_delete.html', {'goal': goal})


@login_required
def savings_goal_deposit(request, pk):
    """Quick deposit / add money to savings goal."""
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = SavingsDepositForm(request.POST)
        if form.is_valid():
            deposit = form.cleaned_data['deposit_amount']
            goal.current_amount += deposit
            goal.save()
            messages.success(request, f"Added ${deposit} to '{goal.name}'! Current saved: ${goal.current_amount}")
        else:
            messages.error(request, "Invalid deposit amount entered.")
    return redirect('finance:savings_goal_list')
