import csv
import os

CSV_FILE = "expenses.csv"
FIELDNAMES = ["date", "amount", "category", "note"]


def init_csv():
    """若檔案不存在，自動建立並寫入表頭。"""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def save_expense(date_str, amount, category, note=""):
    init_csv()
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow({
            "date": date_str,
            "amount": f"{amount:.2f}",
            "category": category,
            "note": note,
        })


if __name__ == "__main__":
    init_csv()
    print(f"'{CSV_FILE}' is ready.")