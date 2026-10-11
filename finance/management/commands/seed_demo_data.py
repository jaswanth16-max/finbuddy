from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from finance.models import Transaction, Budget, SavingsGoal


class Command(BaseCommand):
    help = 'Seeds realistic financial demo data for testing FinBuddy'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='demo', help='Username to seed data for')
        parser.add_argument('--password', type=str, default='Password123!', help='Password for newly created demo user')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']

        user, created = User.objects.get_or_create(username=username, defaults={
            'first_name': 'Alex',
            'last_name': 'Morgan',
            'email': f'{username}@example.com',
            'is_staff': True,
            'is_superuser': True
        })

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created demo user '{username}' with password '{password}'"))
        else:
            self.stdout.write(self.style.WARNING(f"User '{username}' already exists. Appending demo data..."))

        today = timezone.now().date()
        current_month = today.month
        current_year = today.year

        # 1. Seed Income Transactions
        income_samples = [
            ("Monthly Tech Salary", Decimal('5200.00'), 'Salary', today.replace(day=1)),
            ("Freelance UI Design Project", Decimal('1450.00'), 'Freelance', today - timedelta(days=8)),
            ("Quarterly Stock Dividends", Decimal('320.00'), 'Investments', today - timedelta(days=14)),
            ("Consulting Retainer", Decimal('1200.00'), 'Freelance', today - timedelta(days=22)),
            ("Prior Month Tech Salary", Decimal('5200.00'), 'Salary', today - timedelta(days=35)),
            ("Side Project Royalty", Decimal('650.00'), 'Business', today - timedelta(days=45)),
            ("Tech Salary (2 Months Ago)", Decimal('5200.00'), 'Salary', today - timedelta(days=65)),
            ("Freelance Mobile App", Decimal('1800.00'), 'Freelance', today - timedelta(days=75)),
            ("Tech Salary (3 Months Ago)", Decimal('5200.00'), 'Salary', today - timedelta(days=95)),
        ]

        for title, amt, cat, dt in income_samples:
            Transaction.objects.get_or_create(
                user=user,
                title=title,
                date=dt,
                defaults={
                    'amount': amt,
                    'transaction_type': 'INCOME',
                    'category': cat,
                    'description': f'Demo revenue record for {cat}'
                }
            )

        # 2. Seed Expense Transactions
        expense_samples = [
            ("Apartment Rent Payment", Decimal('1850.00'), 'Housing', today.replace(day=2)),
            ("Whole Foods Grocery Run", Decimal('184.50'), 'Groceries', today - timedelta(days=3)),
            ("Electric & Water Utility", Decimal('142.30'), 'Utilities', today - timedelta(days=5)),
            ("High Speed Fiber Internet", Decimal('79.99'), 'Utilities', today - timedelta(days=7)),
            ("Trader Joe's Supermarket", Decimal('126.40'), 'Groceries', today - timedelta(days=10)),
            ("Dinner with Team (Italian Bistro)", Decimal('94.50'), 'Dining Out', today - timedelta(days=11)),
            ("Gasoline & Fuel Refill", Decimal('58.00'), 'Transportation', today - timedelta(days=13)),
            ("Netflix & Spotify Subscriptions", Decimal('34.98'), 'Subscriptions', today - timedelta(days=15)),
            ("Gym Membership Monthly", Decimal('65.00'), 'Personal Care', today - timedelta(days=18)),
            ("Weekend Sushi Dinner", Decimal('82.20'), 'Dining Out', today - timedelta(days=20)),
            ("Dentist Checkup & Cleaning", Decimal('150.00'), 'Healthcare', today - timedelta(days=25)),
            ("Prior Month Rent", Decimal('1850.00'), 'Housing', today - timedelta(days=33)),
            ("Prior Month Groceries", Decimal('460.00'), 'Groceries', today - timedelta(days=40)),
            ("Prior Month Dining & Coffee", Decimal('220.00'), 'Dining Out', today - timedelta(days=42)),
            ("Flight Booking (Summer Trip)", Decimal('420.00'), 'Travel', today - timedelta(days=50)),
            ("Apartment Rent (2 Months Ago)", Decimal('1850.00'), 'Housing', today - timedelta(days=64)),
            ("Groceries (2 Months Ago)", Decimal('480.00'), 'Groceries', today - timedelta(days=68)),
            ("New Running Shoes", Decimal('135.00'), 'Shopping', today - timedelta(days=72)),
        ]

        for title, amt, cat, dt in expense_samples:
            Transaction.objects.get_or_create(
                user=user,
                title=title,
                date=dt,
                defaults={
                    'amount': amt,
                    'transaction_type': 'EXPENSE',
                    'category': cat,
                    'description': f'Demo expense record for {cat}'
                }
            )

        # 3. Seed Monthly Budgets for Current Month
        budget_samples = [
            ("Housing", Decimal('1900.00')),
            ("Groceries", Decimal('600.00')),
            ("Dining Out", Decimal('250.00')),
            ("Utilities", Decimal('250.00')),
            ("Transportation", Decimal('180.00')),
            ("Personal Care", Decimal('120.00')),
            ("Subscriptions", Decimal('50.00')),
        ]

        for cat, limit in budget_samples:
            Budget.objects.get_or_create(
                user=user,
                category=cat,
                month=current_month,
                year=current_year,
                defaults={'amount': limit}
            )

        # 4. Seed Savings Goals
        goal_samples = [
            ("Emergency Rainy Day Fund", Decimal('15000.00'), Decimal('10500.00'), today + timedelta(days=120), "6 months of living expenses reserve."),
            ("New Electric Vehicle Downpayment", Decimal('8000.00'), Decimal('5200.00'), today + timedelta(days=210), "Target downpayment for low APR loan."),
            ("Japan Summer Vacation", Decimal('4500.00'), Decimal('3400.00'), today + timedelta(days=90), "Flights, Ryokan stays, and culinary tour."),
            ("Home Office Equipment Upgrade", Decimal('1200.00'), Decimal('1200.00'), today - timedelta(days=5), "Ergonomic chair and 4K display (Goal Achieved!)."),
        ]

        for name, target, current, target_dt, desc in goal_samples:
            SavingsGoal.objects.get_or_create(
                user=user,
                name=name,
                defaults={
                    'target_amount': target,
                    'current_amount': current,
                    'target_date': target_dt,
                    'description': desc
                }
            )

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded demo transactions, budgets, and savings goals for user '{username}'!"))
