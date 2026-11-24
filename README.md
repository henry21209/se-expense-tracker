# se-expense-tracker

Software Engineering Assignment 1 - A simple command-line expense tracking tool built in Python.

### Installation
Install required dependencies:
```bash
pip install -r requirements.txt
```

### Data Format (`expenses.csv`)
All expenses are stored in `expenses.csv` (UTF-8):
`date,amount,category,note`

### Usage

#### 1. Input Module (Member A)
Run the interactive CLI to add and view expenses:
```bash
python input_expense.py
```
- Validates date format (`YYYY-MM-DD`) and positive amounts.
- Supports preset categories (1-6) or custom category names.

#### 2. Visualization Module (Member B)
Generate an interactive category donut chart and terminal expense summary from `expenses.csv`:
```bash
python visualize.py
```
**Optional Arguments & Interactive Features:**
- **Filter by month (`YYYY-MM`)**: `python visualize.py --month 2026-11`
- **Select initial color theme (`modern`, `morandi`, `dark`)**: `python visualize.py --theme dark`
- **Custom output filename**: `python visualize.py --output custom_chart.png`
- **Interactive Controls**: Use the buttons at the bottom of the chart window to switch themes live (`Modern` / `Morandi` / `Dark Mode`) or click `Save PNG` to export a clean chart image.

### Sample Output
![Expense Pie Chart](pie_chart.png)