# 💳 FinBuddy - Financial Management Platform

> **Tagline:** *“Your Money. Your Goals. Your Control.”*

FinBuddy is a complete, modern, responsive personal financial management website built with **Python Django**, **SQLite**, **Vanilla CSS/HTML5/JavaScript**, **Chart.js**, and **Bootstrap Icons**.

---

## 🌟 Key Features

1. **Modern Landing Page & About Page**: Complete hero section, feature breakdown, financial principles, and call-to-actions.
2. **User Authentication & Data Privacy**: Secure Django registration, login, and logout. All transactions, budgets, and savings goals are strictly isolated per user.
3. **Comprehensive Financial Dashboard**:
   - Dynamic real-time calculation of **Total Income**, **Total Expenses**, **Current Net Balance**, and **Monthly Budget Remaining**.
   - Interactive **Chart.js** visualizations:
     - 6-Month Cashflow dynamic bar chart (Income vs Expenses over time).
     - Income vs Expense doughnut chart.
     - Expense category breakdown doughnut chart.
   - Quick Add Transaction modal & recent transactions table.
   - Active monthly budget progress bars and savings goals tracker.
4. **Transaction Management**:
   - Full CRUD: Add, view, edit, and delete income and expense items.
   - Filter by date range (from/to), category, and transaction type (All, Income, Expense).
   - Real-time search by title and memo/description.
   - Instant calculation of filtered income, expenses, and net cashflow.
5. **Monthly Budget Tracking**:
   - Set monthly spending limits per expense category.
   - Real-time calculation of amount spent and remaining budget allowance.
   - Color-coded progress bars (Normal, Nearing Limit, Exceeded).
   - Automatic visual warning alert banner when spending exceeds budget limits.
6. **Savings Goals Tracker**:
   - Create goal targets with name, target amount, current saved amount, target date, and strategy notes.
   - Visual percentage completion bars.
   - Quick "Deposit / Add Funds" action on each goal.
   - Edit and delete goals.

---

## 🚀 Quick Start Guide (Windows / VS Code)

### 1. Open Terminal in the Project Folder
Open VS Code in `C:\Users\Jaswanth\.gemini\antigravity\scratch\finbuddy` or navigate there in PowerShell:
```powershell
cd C:\Users\Jaswanth\.gemini\antigravity\scratch\finbuddy
```

### 2. Install Dependencies
```powershell
python -m pip install -r requirements.txt
```

### 3. Apply Database Migrations
```powershell
python manage.py makemigrations finance
python manage.py migrate
```

### 4. Seed Demo Data (Optional but Recommended)
Populates a full set of realistic transactions, monthly budgets, savings goals, and creates a demo user account:
```powershell
python manage.py seed_demo_data
```
- **Demo Username:** `demo`
- **Demo Password:** `Password123!`

*(You can also create your own superuser with `python manage.py createsuperuser` or register via the website.)*

### 5. Start the Development Server
```powershell
python manage.py runserver
```

Now open your browser and navigate to:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🗺️ Website Page Routes

| Page | URL Path | Description |
| :--- | :--- | :--- |
| **Home Page** | `http://127.0.0.1:8000/` | Landing page with hero, live preview, features, and CTAs |
| **About Page** | `http://127.0.0.1:8000/about/` | FinBuddy mission, 4 principles, and technology overview |
| **Register** | `http://127.0.0.1:8000/register/` | Create a new user account |
| **Login** | `http://127.0.0.1:8000/login/` | Secure login |
| **Logout** | `http://127.0.0.1:8000/logout/` | Secure logout |
| **Dashboard** | `http://127.0.0.1:8000/dashboard/` | Financial summary cards, Chart.js graphs, and recent records |
| **Transactions** | `http://127.0.0.1:8000/transactions/` | Filterable and searchable ledger of income and expenses |
| **Add Transaction** | `http://127.0.0.1:8000/transactions/add/` | Add a new income or expense transaction |
| **Budgets** | `http://127.0.0.1:8000/budgets/` | Monthly budgets by category with warnings and progress bars |
| **Set Budget** | `http://127.0.0.1:8000/budgets/add/` | Create a monthly category budget limit |
| **Savings Goals** | `http://127.0.0.1:8000/savings/` | Target milestones, visual progress, and quick deposits |
| **Add Goal** | `http://127.0.0.1:8000/savings/add/` | Create a new savings goal |
| **Django Admin** | `http://127.0.0.1:8000/admin/` | Admin panel for models management |

---

## 🛡️ Security & Privacy Features
- **User Isolation**: Every database query filters by `request.user`. Users can only access and modify their own records.
- **CSRF Defense**: All POST forms include Django's `{% csrf_token %}`.
- **Password Security**: Standard PBKDF2 with SHA256 password hashing.
- **Form Validation**: Strict validation for amounts (strictly positive decimal values).
