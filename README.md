# NovaBank — Python Banking Management System

A polished educational banking dashboard built with Python, Streamlit, Pandas, and SQLite.

## Features
- Executive overview with balances, account counts, and charts
- Sample customers and transaction history seeded automatically on first run
- Searchable customer/account directory
- Open new accounts with an opening deposit
- Credit/deposit and debit/withdrawal operations with balance validation
- Internal account transfers with paired transaction ledger entries
- Account activation/deactivation
- Transaction filters and CSV report downloads
- Persistent local SQLite database (`bank.db`)

## Run on Windows

```powershell
# 1. Open this folder in terminal
python -m venv .venv

# 2. Activate the environment
.\.venv\Scripts\Activate.ps1

# 3. Install packages
python -m pip install -r requirements.txt

# 4. Start the app
streamlit run app.py
```

If PowerShell blocks activation, use Command Prompt:
```bat
.venv\Scripts\activate.bat
```

## Sample demo accounts
The app creates these records automatically the first time it runs:

| Customer | Account number | Type | Opening demo balance |
|---|---|---|---:|
| Aarav Sharma | NB1001001 | Savings | ₹84,500.00 |
| Priya Verma | NB1001002 | Current | ₹126,750.50 |
| Kabir Singh | NB1001003 | Savings | ₹42,500.00 |
| Meera Patel | NB1001004 | Salary | ₹97,320.00 |
| Ishaan Gupta | NB1001005 | Savings | ₹15,890.75 |
| Ananya Rao | NB1001006 | Current | ₹211,000.00 |
| Rohan Das | NB1001007 | Salary | ₹63,420.25 |
| Sana Khan | NB1001008 | Savings | ₹28,750.00 |

These are fictional sample records. No real bank or payment network is connected.

## Data storage
`bank.db` is created in the project folder. Do not delete it unless you want to reset the demo database. Sample data is only seeded when the customer table is empty.

## Important security note
This is a learning/demo application, not production banking software. It intentionally has no login/authentication and should not be exposed publicly or used for real customer data. A production system needs secure authentication, role-based access, encryption, audit logging, robust input validation, backups, monitoring, and compliance/security review.
