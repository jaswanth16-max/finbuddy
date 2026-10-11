from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from finance.models import Transaction, Budget, SavingsGoal


class FinanceModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='TestPassword123!')
        self.today = timezone.now().date()

    def test_budget_calculations(self):
        # Create budget for Groceries: $500 limit
        budget = Budget.objects.create(
            user=self.user,
            category='Groceries',
            amount=Decimal('500.00'),
            month=self.today.month,
            year=self.today.year
        )

        # Before any transactions
        self.assertEqual(budget.get_spent_amount(), Decimal('0.00'))
        self.assertEqual(budget.get_remaining_amount(), Decimal('500.00'))
        self.assertEqual(budget.get_percentage_spent(), 0.0)
        self.assertFalse(budget.is_exceeded())

        # Add transaction of $200
        Transaction.objects.create(
            user=self.user,
            title='Supermarket',
            amount=Decimal('200.00'),
            transaction_type='EXPENSE',
            category='Groceries',
            date=self.today
        )

        self.assertEqual(budget.get_spent_amount(), Decimal('200.00'))
        self.assertEqual(budget.get_remaining_amount(), Decimal('300.00'))
        self.assertEqual(budget.get_percentage_spent(), 40.0)
        self.assertFalse(budget.is_exceeded())

        # Add transaction of $350 (Total spent: $550, exceeds $500 limit)
        Transaction.objects.create(
            user=self.user,
            title='Bulk Store',
            amount=Decimal('350.00'),
            transaction_type='EXPENSE',
            category='Groceries',
            date=self.today
        )

        self.assertEqual(budget.get_spent_amount(), Decimal('550.00'))
        self.assertEqual(budget.get_remaining_amount(), Decimal('-50.00'))
        self.assertEqual(budget.get_percentage_spent(), 110.0)
        self.assertTrue(budget.is_exceeded())

    def test_savings_goal_calculations(self):
        goal = SavingsGoal.objects.create(
            user=self.user,
            name='Vacation Fund',
            target_amount=Decimal('2000.00'),
            current_amount=Decimal('500.00')
        )

        self.assertEqual(goal.get_percentage(), 25.0)
        self.assertEqual(goal.get_remaining_amount(), Decimal('1500.00'))
        self.assertFalse(goal.is_completed())

        goal.current_amount = Decimal('2000.00')
        goal.save()
        self.assertEqual(goal.get_percentage(), 100.0)
        self.assertEqual(goal.get_remaining_amount(), Decimal('0.00'))
        self.assertTrue(goal.is_completed())


class FinanceViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123', email='test@example.com')
        self.other_user = User.objects.create_user(username='otheruser', password='password123')

    def test_public_pages(self):
        response = self.client.get(reverse('finance:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your Money. Your Goals. Your Control.")

        response = self.client.get(reverse('finance:about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "About FinBuddy")

    def test_auth_protection(self):
        # Unauthenticated users should be redirected to login
        response = self.client.get(reverse('finance:dashboard'))
        self.assertRedirects(response, f"{reverse('finance:login')}?next={reverse('finance:dashboard')}")

        response = self.client.get(reverse('finance:transactions_list'))
        self.assertRedirects(response, f"{reverse('finance:login')}?next={reverse('finance:transactions_list')}")

    def test_dashboard_with_authenticated_user(self):
        self.client.login(username='testuser', password='password123')

        # Add sample data
        today = timezone.now().date()
        Transaction.objects.create(
            user=self.user,
            title='Salary',
            amount=Decimal('3000.00'),
            transaction_type='INCOME',
            category='Salary',
            date=today
        )
        Transaction.objects.create(
            user=self.user,
            title='Rent',
            amount=Decimal('1000.00'),
            transaction_type='EXPENSE',
            category='Housing',
            date=today
        )

        response = self.client.get(reverse('finance:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_income'], Decimal('3000.00'))
        self.assertEqual(response.context['total_expenses'], Decimal('1000.00'))
        self.assertEqual(response.context['current_balance'], Decimal('2000.00'))
        self.assertContains(response, "3000.00")
        self.assertContains(response, "1000.00")

    def test_data_isolation(self):
        # Create a transaction belonging to other_user
        t_other = Transaction.objects.create(
            user=self.other_user,
            title='Secret Transaction',
            amount=Decimal('999.00'),
            transaction_type='EXPENSE',
            category='Other Expense',
            date=timezone.now().date()
        )

        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('finance:transactions_list'))
        self.assertNotContains(response, 'Secret Transaction')

        # Attempt to edit or delete other_user's transaction should return 404
        edit_response = self.client.get(reverse('finance:transaction_update', args=[t_other.pk]))
        self.assertEqual(edit_response.status_code, 404)

        delete_response = self.client.post(reverse('finance:transaction_delete', args=[t_other.pk]))
        self.assertEqual(delete_response.status_code, 404)

    def test_transaction_crud(self):
        self.client.login(username='testuser', password='password123')

        # Create transaction
        add_url = reverse('finance:transaction_create')
        post_data = {
            'title': 'New Laptop',
            'amount': '1250.00',
            'transaction_type': 'EXPENSE',
            'category': 'Shopping',
            'date': str(timezone.now().date()),
            'description': 'Work machine'
        }
        res = self.client.post(add_url, post_data)
        self.assertEqual(res.status_code, 302)

        trans = Transaction.objects.filter(user=self.user, title='New Laptop').first()
        self.assertIsNotNone(trans)
        self.assertEqual(trans.amount, Decimal('1250.00'))

        # Edit transaction
        edit_url = reverse('finance:transaction_update', args=[trans.pk])
        edit_data = post_data.copy()
        edit_data['amount'] = '1199.00'
        res = self.client.post(edit_url, edit_data)
        self.assertEqual(res.status_code, 302)
        trans.refresh_from_db()
        self.assertEqual(trans.amount, Decimal('1199.00'))

        # Delete transaction
        delete_url = reverse('finance:transaction_delete', args=[trans.pk])
        res = self.client.post(delete_url)
        self.assertEqual(res.status_code, 302)
        self.assertFalse(Transaction.objects.filter(pk=trans.pk).exists())

    def test_savings_deposit(self):
        self.client.login(username='testuser', password='password123')

        goal = SavingsGoal.objects.create(
            user=self.user,
            name='Emergency Fund',
            target_amount=Decimal('5000.00'),
            current_amount=Decimal('1000.00')
        )

        deposit_url = reverse('finance:savings_goal_deposit', args=[goal.pk])
        res = self.client.post(deposit_url, {'deposit_amount': '500.00'})
        self.assertEqual(res.status_code, 302)

        goal.refresh_from_db()
        self.assertEqual(goal.current_amount, Decimal('1500.00'))
