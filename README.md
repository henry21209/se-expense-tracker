# se-expense-tracker

Software Engineering Assignment 1 - A simple command-line expense tracking tool built in Python.

### Data Format (`expenses.csv`)
All expenses are stored in `expenses.csv` (UTF-8):
`date,amount,category,note`

### 1. Input Module (Member A)
Run the interactive CLI to add and view expenses:
```bash
python input_expense.py
```
- Validates date format (`YYYY-MM-DD`) and positive amounts.
- Supports preset categories (1-6) or custom category names.