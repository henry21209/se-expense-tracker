import csv
import os
from datetime import datetime

CSV_FILE = "expenses.csv"
FIELDNAMES = ["date", "amount", "category", "note"]
CATEGORIES = ["Food", "Transport", "Entertainment", "Utilities", "Shopping", "Other"]


def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def get_valid_date():
    today_str = datetime.now().strftime("%Y-%m-%d")
    while True:
        raw = input(f"Enter date (YYYY-MM-DD) [default: {today_str}]: ").strip()
        if not raw:
            return today_str
        try:
            datetime.strptime(raw, "%Y-%m-%d")
            return raw
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD (e.g., 2026-11-25).")


def get_valid_amount():
    while True:
        raw = input("Enter amount: ").strip()
        try:
            val = float(raw)
            if val <= 0:
                print("Amount must be greater than 0.")
                continue
            return val
        except ValueError:
            print("Invalid number. Please enter a positive number.")


def get_valid_category():
    print("Select category:")
    for idx, cat in enumerate(CATEGORIES, start=1):
        print(f"  {idx}. {cat}")
    while True:
        choice = input("Enter number (1-6) or custom category name: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(CATEGORIES):
            return CATEGORIES[int(choice) - 1]
        if choice:
            return choice.title()
        print("Category cannot be empty.")


def add_expense_interactive():
    date_str = get_valid_date()
    amount = get_valid_amount()
    category = get_valid_category()
    note = input("Enter note (optional, press Enter to skip): ").strip()

    init_csv()
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow({
            "date": date_str,
            "amount": f"{amount:.2f}",
            "category": category,
            "note": note,
        })
    print(f"Saved: [{date_str}] {category} - ${amount:.2f} ({note})\n")


def view_expenses():
    if not os.path.exists(CSV_FILE):
        print("No expenses recorded yet.\n")
        return
    with open(CSV_FILE, mode="r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        if not rows:
            print("No expenses recorded yet.\n")
            return
        print("\n--- Recorded Expenses ---")
        for i, row in enumerate(rows, start=1):
            note_display = f" | Note: {row['note']}" if row.get("note") else ""
            print(f"{i}. {row['date']} | {row['category']:<13} | ${float(row['amount']):>8.2f}{note_display}")
        print("-------------------------\n")


def main():
    init_csv()
    while True:
        print("=== Expense Tracker (Input Module) ===")
        print("1. Add new expense")
        print("2. View all expenses")
        print("3. Exit")
        cmd = input("Choose an option (1-3): ").strip()
        if cmd == "1":
            add_expense_interactive()
        elif cmd == "2":
            view_expenses()
        elif cmd == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid option, please choose 1, 2, or 3.\n")


if __name__ == "__main__":
    main()