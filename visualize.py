import csv
import os
from collections import defaultdict
import matplotlib.pyplot as plt

CSV_FILE = "expenses.csv"
OUTPUT_IMAGE = "pie_chart.png"


def load_expenses_by_category(filepath=CSV_FILE):
    if not os.path.exists(filepath):
        print(f"Error: '{filepath}' not found. Please add expenses first.")
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


def generate_pie_chart(totals, output_image=OUTPUT_IMAGE):
    if not totals:
        print("No valid expense data available to plot.")
        return

    # 依金額由大到小排序，讓圓餅圖視覺更整齊
    sorted_items = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    categories = [item[0] for item in sorted_items]
    amounts = [item[1] for item in sorted_items]
    total_spent = sum(amounts)

    labels = [f"{cat}\n(${amt:.2f})" for cat, amt in zip(categories, amounts)]

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        amounts,
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.75,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5}
    )

    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_weight("bold")

    ax.set_title(f"Expenses by Category (Total: ${total_spent:.2f})", fontsize=14, fontweight="bold", pad=16)
    ax.axis("equal")

    plt.tight_layout()
    plt.savefig(output_image, dpi=300)
    print(f"Pie chart saved to '{output_image}'.")
    plt.show()


def main():
    totals = load_expenses_by_category()
    generate_pie_chart(totals)


if __name__ == "__main__":
    main()