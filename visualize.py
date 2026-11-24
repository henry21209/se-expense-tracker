import argparse
import csv
import os
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

CSV_FILE = "expenses.csv"
OUTPUT_IMAGE = "pie_chart.png"

# 三組內建配色主題
THEMES = {
    "modern": {
        "name": "Modern",
        "bg": "#FAFAFA",
        "text": "#2C3E50",
        "title": "#1A252F",
        "pct_color": "#FFFFFF",
        "colors": [
            "#4E79A7", "#F28E2B", "#E15759", "#76B7B2",
            "#59A14F", "#EDC948", "#B07AA1", "#FF9DA7"
        ],
    },
    "morandi": {
        "name": "Morandi",
        "bg": "#F7F5F2",
        "text": "#4A4642",
        "title": "#363330",
        "pct_color": "#FFFFFF",
        "colors": [
            "#8E9AAF", "#CBC0D3", "#B5838D", "#A3B18A",
            "#D4A373", "#9C89B8", "#B8B8AA", "#E0AFA0"
        ],
    },
    "dark": {
        "name": "Dark Mode",
        "bg": "#1E1E2E",
        "text": "#E0E6ED",
        "title": "#FFFFFF",
        "pct_color": "#1E1E2E",
        "colors": [
            "#89B4FA", "#FAB387", "#F38BA8", "#94E2D5",
            "#A6E3A1", "#F9E2AF", "#CBA6F7", "#F5C2E7"
        ],
    },
}


def load_expenses_by_category(filepath=CSV_FILE, month_filter=None):
    if not os.path.exists(filepath):
        print(f"Error: '{filepath}' not found. Please add expenses first.")
        return {}

    totals = defaultdict(float)
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                date_str = row["date"].strip()
                if month_filter and not date_str.startswith(month_filter):
                    continue
                category = row["category"].strip()
                amount = float(row["amount"])
                if category and amount > 0:
                    totals[category] += amount
            except (KeyError, ValueError):
                continue

    return dict(totals)


def print_summary_table(totals, title_suffix):
    if not totals:
        return
    sorted_items = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    total_spent = sum(totals.values())

    print(f"\n=== Expense Summary ({title_suffix}) ===")
    print(f"{'Category':<16} {'Amount':>10} {'Share':>8}")
    print("-" * 36)
    for cat, amt in sorted_items:
        pct = (amt / total_spent) * 100
        print(f"{cat:<16} ${amt:>9,.2f} {pct:>7.1f}%")
    print("-" * 36)
    print(f"{'TOTAL':<16} ${total_spent:>9,.2f} {'100.0%':>8}\n")


def generate_interactive_chart(
    totals,
    output_image=OUTPUT_IMAGE,
    title_suffix="All Time",
    initial_theme="modern",
):
    if not totals:
        print("No valid expense data available to plot.")
        return

    sorted_items = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    categories = [item[0] for item in sorted_items]
    amounts = [item[1] for item in sorted_items]
    total_spent = sum(amounts)
    explode = [0.05 if i == 0 else 0 for i in range(len(amounts))]

    # 加寬畫布，並手動配置圓餅圖區域（左 4%、底 17%、寬 48%、高 72%）
    # 右側保留將近一半的寬度給圖例，徹底解決視窗裁切問題
    fig = plt.figure(figsize=(10.5, 6), dpi=115)
    try:
        fig.canvas.manager.set_window_title("Expense Tracker - Visualization")
    except AttributeError:
        pass

    ax = fig.add_axes([0.04, 0.17, 0.48, 0.72])
    button_axes = []

    def draw_chart(theme_key):
        theme = THEMES[theme_key]
        ax.clear()
        fig.patch.set_facecolor(theme["bg"])
        ax.set_facecolor(theme["bg"])

        colors = [theme["colors"][i % len(theme["colors"])] for i in range(len(amounts))]

        wedges, texts, autotexts = ax.pie(
            amounts,
            explode=explode,
            colors=colors,
            autopct=lambda pct: f"{pct:.1f}%" if pct >= 4 else "",
            startangle=140,
            pctdistance=0.78,
            wedgeprops={"width": 0.42, "edgecolor": theme["bg"], "linewidth": 2.5},
        )

        for autotext in autotexts:
            autotext.set_color(theme["pct_color"])
            autotext.set_fontsize(9.5)
            autotext.set_weight("bold")

        ax.text(
            0, 0,
            f"Total Spent\n${total_spent:,.2f}",
            ha="center", va="center",
            fontsize=13, fontweight="bold", color=theme["text"],
        )

        legend_labels = [
            f"{cat:<14} ${amt:>8,.2f} ({amt / total_spent * 100:>5.1f}%)"
            for cat, amt in zip(categories, amounts)
        ]
        legend = ax.legend(
            wedges,
            legend_labels,
            title="Category Breakdown",
            title_fontsize=11,
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            frameon=False,
            prop={"family": "monospace", "size": 9.5},
        )
        plt.setp(legend.get_title(), color=theme["title"], fontweight="bold")
        for text in legend.get_texts():
            text.set_color(theme["text"])

        ax.set_title(
            f"Expense Distribution ({title_suffix})",
            fontsize=15, fontweight="bold", color=theme["title"], pad=16,
        )
        ax.axis("equal")
        fig.canvas.draw_idle()

    def save_clean_png(event=None):
        # 存檔前暫時隱藏按鈕列，讓輸出的 pie_chart.png 不會出現按鈕
        for b_ax in button_axes:
            b_ax.set_visible(False)
        fig.savefig(output_image, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
        for b_ax in button_axes:
            b_ax.set_visible(True)
        fig.canvas.draw_idle()
        print(f"Chart saved to '{output_image}'.")

    # 建立底部互動按鈕列（位置：[左, 下, 寬, 高]）
    btn_specs = [
        ("Modern",    [0.10, 0.04, 0.14, 0.065], lambda e: draw_chart("modern"),  "#E2E8F0", "#CBD5E1"),
        ("Morandi",   [0.26, 0.04, 0.14, 0.065], lambda e: draw_chart("morandi"), "#E8DFD8", "#D6C7BC"),
        ("Dark Mode", [0.42, 0.04, 0.14, 0.065], lambda e: draw_chart("dark"),    "#334155", "#475569"),
        ("Save PNG",  [0.64, 0.04, 0.16, 0.065], save_clean_png,                  "#D1FAE5", "#A7F3D0"),
    ]

    # 必須把 Button 物件存在 list 裡，避免被 Python 垃圾回收導致點擊失效
    buttons = []
    for label, rect, callback, bg_col, hover_col in btn_specs:
        b_ax = fig.add_axes(rect)
        button_axes.append(b_ax)
        btn = Button(b_ax, label, color=bg_col, hovercolor=hover_col)
        btn.label.set_fontsize(9.5)
        btn.label.set_fontweight("bold")
        if label == "Dark Mode":
            btn.label.set_color("#FFFFFF")
        btn.on_clicked(callback)
        buttons.append(btn)

    draw_chart(initial_theme)
    save_clean_png()  # 啟動時先自動匯出一份預設主題的 PNG
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Generate a category expense donut chart.")
    parser.add_argument(
        "--month",
        type=str,
        default=None,
        help="Filter expenses by month in YYYY-MM format (e.g., 2026-11)",
    )
    parser.add_argument(
        "--theme",
        type=str,
        choices=["modern", "morandi", "dark"],
        default="modern",
        help="Initial color theme (modern, morandi, dark)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=OUTPUT_IMAGE,
        help="Output image filename (default: pie_chart.png)",
    )
    args = parser.parse_args()

    title_suffix = args.month if args.month else "All Time"
    totals = load_expenses_by_category(month_filter=args.month)
    print_summary_table(totals, title_suffix)
    generate_interactive_chart(
        totals,
        output_image=args.output,
        title_suffix=title_suffix,
        initial_theme=args.theme,
    )


if __name__ == "__main__":
    main()