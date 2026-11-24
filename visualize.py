import csv
import os
from collections import defaultdict

CSV_FILE = "expenses.csv"


def load_expenses_by_category(filepath=CSV_FILE):
    if not os.path.exists(filepath):
        print(f"Error: '{filepath}' not found. Please run the input module first.")
        return {}

    totals = defaultdict(float)
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                category = row["category"].strip()
                amount = float(row["amount"])
                if category and amount > 0:
                    totals[category] += amount
            except (KeyError, ValueError):
                continue

    return dict(totals)


if __name__ == "__main__":
    data = load_expenses_by_category()
    print("Category Totals:", data)