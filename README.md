# Payroll Reconciliation System

This application helps finance teams reconcile employees' expected net pay against actual bank payments to identify fully paid, underpaid, overpaid and unpaid employees.

## Project Features

- Employee management: Create, view, update and delete employee records.
- Payroll records: Store employees' expected net pay.
- Bank transactions: Record actual payments from bank statements.
- Payroll reconciliation: Compare expected net pay against actual payments.
- Payment classification: Identify Fully Paid, Underpaid, Overpaid and Not Paid employees.
- Unmatched transactions: Identify bank payments linked to employee IDs not found in the employee database.
- Reconciliation dashboard: Display payment summaries and exceptions.
- Database storage: SQLite to preserve records between application sessions.
- Excel export: Export reconciliation results for further analysis.


## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/NYAMAIK/payroll_reconciliation_system
```

### 2. Navigate to the project folder

```bash
cd payroll_reconciliation_system
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

Windows (Git Bash):

```bash
source .venv/Scripts/activate
```

Windows (Command Prompt):

```cmd
.venv\Scripts\activate
```

### 5. Install the required packages

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
streamlit run app.py
```

The application will open in your web browser.

