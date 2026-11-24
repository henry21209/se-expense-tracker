import csv
import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# 直接匯入組員 A 與組員 B 的模組，維持模組化架構
from input_expense import CATEGORIES, CSV_FILE, FIELDNAMES, init_csv
from visualize import OUTPUT_IMAGE, THEMES, load_expenses_by_category


class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Integrated GUI")
        self.root.geometry("1180x680")
        self.root.minsize(1040, 600)
        self.root.configure(bg="#F1F5F9")

        self.current_theme = "modern"
        self.month_var = tk.StringVar(value="All Time")

        init_csv()
        self._configure_styles()
        self._build_ui()
        self.refresh_all()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background="#F1F5F9")
        style.configure("Card.TFrame", background="#FFFFFF", relief="flat")
        style.configure(
            "Title.TLabel",
            background="#FFFFFF",
            foreground="#0F172A",
            font=("Segoe UI", 13, "bold"),
        )
        style.configure(
            "Field.TLabel",
            background="#FFFFFF",
            foreground="#334155",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Primary.TButton",
            background="#2563EB",
            foreground="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 7),
            borderwidth=0,
        )
        style.map("Primary.TButton", background=[("active", "#1D4ED8")])

        style.configure(
            "Secondary.TButton",
            background="#E2E8F0",
            foreground="#1E293B",
            font=("Segoe UI", 9, "bold"),
            padding=(10, 5),
            borderwidth=0,
        )
        style.map("Secondary.TButton", background=[("active", "#CBD5E1")])

        style.configure(
            "Treeview",
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            foreground="#1E293B",
            rowheight=26,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Treeview.Heading",
            background="#E2E8F0",
            foreground="#0F172A",
            font=("Segoe UI", 9, "bold"),
        )

    def _build_ui(self):
        # 頂部標題列
        header = tk.Frame(self.root, bg="#0F172A", height=54)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header,
            text="Expense Tracker  |  Input & Visualization Suite",
            bg="#0F172A",
            fg="#F8FAFC",
            font=("Segoe UI", 14, "bold"),
        ).pack(side="left", padx=20)

        # 主內容區（左右分割）
        main_frame = ttk.Frame(self.root, padding=14)
        main_frame.pack(fill="both", expand=True)

        # === 左側：輸入表單 + 紀錄列表 ===
        left_panel = ttk.Frame(main_frame, width=420)
        left_panel.pack(side="left", fill="y", padx=(0, 12))
        left_panel.pack_propagate(False)

        # 表單卡片
        form_card = ttk.Frame(left_panel, style="Card.TFrame", padding=16)
        form_card.pack(fill="x", pady=(0, 12))

        ttk.Label(form_card, text="Add New Expense", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 12)
        )

        # Date
        ttk.Label(form_card, text="Date (YYYY-MM-DD)", style="Field.TLabel").grid(
            row=1, column=0, sticky="w", pady=4
        )
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(form_card, textvariable=self.date_var, width=26).grid(
            row=1, column=1, sticky="ew", pady=4, padx=(10, 0)
        )

        # Amount
        ttk.Label(form_card, text="Amount ($)", style="Field.TLabel").grid(
            row=2, column=0, sticky="w", pady=4
        )
        self.amount_var = tk.StringVar()
        ttk.Entry(form_card, textvariable=self.amount_var, width=26).grid(
            row=2, column=1, sticky="ew", pady=4, padx=(10, 0)
        )

        # Category
        ttk.Label(form_card, text="Category", style="Field.TLabel").grid(
            row=3, column=0, sticky="w", pady=4
        )
        self.category_var = tk.StringVar(value=CATEGORIES[0])
        cat_combo = ttk.Combobox(
            form_card, textvariable=self.category_var, values=CATEGORIES, width=24
        )
        cat_combo.grid(row=3, column=1, sticky="ew", pady=4, padx=(10, 0))

        # Note
        ttk.Label(form_card, text="Note (Optional)", style="Field.TLabel").grid(
            row=4, column=0, sticky="w", pady=4
        )
        self.note_var = tk.StringVar()
        ttk.Entry(form_card, textvariable=self.note_var, width=26).grid(
            row=4, column=1, sticky="ew", pady=4, padx=(10, 0)
        )

        form_card.columnconfigure(1, weight=1)

        ttk.Button(
            form_card,
            text="+ Add Expense",
            style="Primary.TButton",
            command=self.add_expense,
        ).grid(row=5, column=0, columnspan=2, sticky="ew", pady=(14, 0))

        # 紀錄表格卡片
        table_card = ttk.Frame(left_panel, style="Card.TFrame", padding=12)
        table_card.pack(fill="both", expand=True)

        ttk.Label(table_card, text="Recent Expenses", style="Title.TLabel").pack(
            anchor="w", pady=(0, 8)
        )

        cols = ("date", "category", "amount", "note")
        self.tree = ttk.Treeview(table_card, columns=cols, show="headings")
        self.tree.heading("date", text="Date")
        self.tree.heading("category", text="Category")
        self.tree.heading("amount", text="Amount")
        self.tree.heading("note", text="Note")

        self.tree.column("date", width=86, anchor="center")
        self.tree.column("category", width=95, anchor="w")
        self.tree.column("amount", width=72, anchor="e")
        self.tree.column("note", width=115, anchor="w")

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # === 右側：即時甜甜圈圖 + 控制列 ===
        right_panel = ttk.Frame(main_frame, style="Card.TFrame", padding=14)
        right_panel.pack(side="right", fill="both", expand=True)

        # 頂部控制列（月份篩選 + 主題按鈕 + 存檔）
        ctrl_bar = ttk.Frame(right_panel, style="Card.TFrame")
        ctrl_bar.pack(fill="x", pady=(0, 8))

        ttk.Label(ctrl_bar, text="Filter Month:", style="Field.TLabel").pack(
            side="left", padx=(0, 6)
        )
        self.month_combo = ttk.Combobox(
            ctrl_bar, textvariable=self.month_var, state="readonly", width=12
        )
        self.month_combo.pack(side="left", padx=(0, 14))
        self.month_combo.bind("<<ComboboxSelected>>", lambda e: self.draw_chart())

        ttk.Button(
            ctrl_bar,
            text="Modern",
            style="Secondary.TButton",
            command=lambda: self.set_theme("modern"),
        ).pack(side="left", padx=3)
        ttk.Button(
            ctrl_bar,
            text="Morandi",
            style="Secondary.TButton",
            command=lambda: self.set_theme("morandi"),
        ).pack(side="left", padx=3)
        ttk.Button(
            ctrl_bar,
            text="Dark",
            style="Secondary.TButton",
            command=lambda: self.set_theme("dark"),
        ).pack(side="left", padx=3)

        ttk.Button(
            ctrl_bar,
            text="Save PNG",
            style="Primary.TButton",
            command=self.save_png,
        ).pack(side="right")

        # 內嵌 Matplotlib 畫布
        self.fig = Figure(figsize=(7.2, 5.2), dpi=105)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_panel)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def add_expense(self):
        date_str = self.date_var.get().strip()
        amount_str = self.amount_var.get().strip()
        category = self.category_var.get().strip().title()
        note = self.note_var.get().strip()

        # 日期驗證
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Date", "Please use YYYY-MM-DD format (e.g., 2026-11-25).")
            return

        # 金額驗證
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Amount", "Amount must be a positive number.")
            return

        if not category:
            messagebox.showerror("Invalid Category", "Category cannot be empty.")
            return

        init_csv()
        with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writerow({
                "date": date_str,
                "amount": f"{amount:.2f}",
                "category": category,
                "note": note,
            })

        self.amount_var.set("")
        self.note_var.set("")
        self.refresh_all()

    def refresh_all(self):
        self._load_table_and_months()
        self.draw_chart()

    def _load_table_and_months(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        months = set()
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, mode="r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
                for row in reversed(rows):  # 最新紀錄顯示在最上方
                    date_val = row.get("date", "").strip()
                    if len(date_val) >= 7:
                        months.add(date_val[:7])
                    self.tree.insert(
                        "",
                        "end",
                        values=(
                            date_val,
                            row.get("category", ""),
                            f"${float(row.get('amount', 0)):,.2f}",
                            row.get("note", ""),
                        ),
                    )

        month_options = ["All Time"] + sorted(months, reverse=True)
        self.month_combo["values"] = month_options
        if self.month_var.get() not in month_options:
            self.month_var.set("All Time")

    def set_theme(self, theme_key):
        self.current_theme = theme_key
        self.draw_chart()

    def draw_chart(self):
        selected_month = self.month_var.get()
        month_filter = None if selected_month == "All Time" else selected_month
        totals = load_expenses_by_category(CSV_FILE, month_filter=month_filter)

        theme = THEMES[self.current_theme]
        self.fig.clear()
        self.fig.patch.set_facecolor(theme["bg"])

        if not totals:
            ax = self.fig.add_subplot(111)
            ax.set_facecolor(theme["bg"])
            ax.axis("off")
            ax.text(
                0.5, 0.5, "No expenses recorded for this period.",
                ha="center", va="center", fontsize=12, color=theme["text"],
            )
            self.canvas.draw()
            return

        sorted_items = sorted(totals.items(), key=lambda x: x[1], reverse=True)
        categories = [item[0] for item in sorted_items]
        amounts = [item[1] for item in sorted_items]
        total_spent = sum(amounts)
        explode = [0.05 if i == 0 else 0 for i in range(len(amounts))]
        colors = [theme["colors"][i % len(theme["colors"])] for i in range(len(amounts))]

        # 左側放甜甜圈，右側留白給圖例防止裁切
        ax = self.fig.add_axes([0.03, 0.08, 0.50, 0.80])
        ax.set_facecolor(theme["bg"])

        wedges, _, autotexts = ax.pie(
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
            autotext.set_fontsize(9)
            autotext.set_weight("bold")

        ax.text(
            0, 0,
            f"Total Spent\n${total_spent:,.2f}",
            ha="center", va="center",
            fontsize=12, fontweight="bold", color=theme["text"],
        )

        legend_labels = [
            f"{cat:<13} ${amt:>8,.2f} ({amt / total_spent * 100:>5.1f}%)"
            for cat, amt in zip(categories, amounts)
        ]
        legend = ax.legend(
            wedges,
            legend_labels,
            title="Category Breakdown",
            title_fontsize=10.5,
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            frameon=False,
            prop={"family": "monospace", "size": 9},
        )
        legend_title = legend.get_title()
        legend_title.set_color(theme["title"])
        legend_title.set_fontweight("bold")
        for text in legend.get_texts():
            text.set_color(theme["text"])

        ax.set_title(
            f"Expense Distribution ({selected_month})",
            fontsize=14, fontweight="bold", color=theme["title"], pad=14,
        )
        ax.axis("equal")
        self.canvas.draw()

    def save_png(self):
        self.fig.savefig(
            OUTPUT_IMAGE,
            dpi=300,
            bbox_inches="tight",
            facecolor=self.fig.get_facecolor(),
        )
        messagebox.showinfo("Saved", f"Chart exported to '{OUTPUT_IMAGE}'.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()