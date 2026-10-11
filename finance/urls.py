from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    # Public Pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Transactions
    path('transactions/', views.transactions_list, name='transactions_list'),
    path('transactions/add/', views.transaction_create, name='transaction_create'),
    path('transactions/<int:pk>/edit/', views.transaction_update, name='transaction_update'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),

    # Budgets
    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/add/', views.budget_create, name='budget_create'),
    path('budgets/<int:pk>/edit/', views.budget_update, name='budget_update'),
    path('budgets/<int:pk>/delete/', views.budget_delete, name='budget_delete'),

    # Savings Goals
    path('savings/', views.savings_goal_list, name='savings_goal_list'),
    path('savings/add/', views.savings_goal_create, name='savings_goal_create'),
    path('savings/<int:pk>/edit/', views.savings_goal_update, name='savings_goal_update'),
    path('savings/<int:pk>/delete/', views.savings_goal_delete, name='savings_goal_delete'),
    path('savings/<int:pk>/deposit/', views.savings_goal_deposit, name='savings_goal_deposit'),
]
