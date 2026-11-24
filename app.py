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
        self.root.geometry("1200x700")
        self.root.minsize(1060, 620)
        self.root.configure(bg="#F1F5F9")

        self.rows = []
        self.current_theme = "modern"
        self.budget_limit = 1000.0
        self.month_var = tk.StringVar(value="All Time")
        self.budget_var = tk.StringVar(value="1000")
        self.budget_status_var = tk.StringVar(value="")

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
            font=("Segoe UI", 12, "bold"),
        )
        style.configure(
            "Field.TLabel",
            background="#FFFFFF",
            foreground="#334155",
            font=("Segoe UI", 9),
        )
        style.configure(
            "Primary.TButton",
            background="#2563EB",
            foreground="#FFFFFF",
            font=("Segoe UI", 9, "bold"),
            padding=(12, 6),
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
            "Danger.TButton",
            background="#FEE2E2",
            foreground="#B91C1C",
            font=("Segoe UI", 9, "bold"),
            padding=(10, 5),
            borderwidth=0,
        )
        style.map("Danger.TButton", background=[("active", "#FECACA")])

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

        # 三段式預算進度條樣式（安全綠 / 警戒橘 / 超支紅）
        style.configure(
            "Green.Horizontal.TProgressbar",
            troughcolor="#E2E8F0",
            background="#10B981",
            bordercolor="#E2E8F0",
            lightcolor="#10B981",
            darkcolor="#10B981",
            thickness=14,
        )
        style.configure(
            "Amber.Horizontal.TProgressbar",
            troughcolor="#E2E8F0",
            background="#F59E0B",
            bordercolor="#E2E8F0",
            lightcolor="#F59E0B",
            darkcolor="#F59E0B",
            thickness=14,
        )
        style.configure(
            "Red.Horizontal.TProgressbar",
            troughcolor="#FEE2E2",
            background="#EF4444",
            bordercolor="#FEE2E2",
            lightcolor="#EF4444",
            darkcolor="#EF4444",
            thickness=14,
        )

    def _build_ui(self):
        # 頂部標題列
        header = tk.Frame(self.root, bg="#0F172A", height=52)
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

        # === 左側：輸入表單 + 紀錄列表（支援雙擊編輯與刪除） ===
        left_panel = ttk.Frame(main_frame, width=430)
        left_panel.pack(side="left", fill="y", padx=(0, 12))
        left_panel.pack_propagate(False)

        # 表單卡片
        form_card = ttk.Frame(left_panel, style="Card.TFrame", padding=15)
        form_card.pack(fill="x", pady=(0, 12))

        ttk.Label(form_card, text="Add New Expense", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10)
        )

        ttk.Label(form_card, text="Date (YYYY-MM-DD)", style="Field.TLabel").grid(
            row=1, column=0, sticky="w", pady=4
        )
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(form_card, textvariable=self.date_var, width=26).grid(
            row=1, column=1, sticky="ew", pady=4, padx=(10, 0)
        )

        ttk.Label(form_card, text="Amount ($)", style="Field.TLabel").grid(
            row=2, column=0, sticky="w", pady=4
        )
        self.amount_var = tk.StringVar()
        ttk.Entry(form_card, textvariable=self.amount_var, width=26).grid(
            row=2, column=1, sticky="ew", pady=4, padx=(10, 0)
        )

        ttk.Label(form_card, text="Category", style="Field.TLabel").grid(
            row=3, column=0, sticky="w", pady=4
        )
        self.category_var = tk.StringVar(value=CATEGORIES[0])
        ttk.Combobox(
            form_card, textvariable=self.category_var, values=CATEGORIES, width=24
        ).grid(row=3, column=1, sticky="ew", pady=4, padx=(10, 0))

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
        ).grid(row=5, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        # 紀錄表格卡片
        table_card = ttk.Frame(left_panel, style="Card.TFrame", padding=12)
        table_card.pack(fill="both", expand=True)

        table_header = ttk.Frame(table_card, style="Card.TFrame")
        table_header.pack(fill="x", pady=(0, 6))
        ttk.Label(table_header, text="Recent Expenses", style="Title.TLabel").pack(
            side="left"
        )
        tk.Label(
            table_header,
            text="(Double-click row to edit)",
            bg="#FFFFFF",
            fg="#64748B",
            font=("Segoe UI", 8),
        ).pack(side="right")

        tree_container = ttk.Frame(table_card, style="Card.TFrame")
        tree_container.pack(fill="both", expand=True)

        cols = ("date", "category", "amount", "note")
        self.tree = ttk.Treeview(
            tree_container, columns=cols, show="headings", selectmode="browse"
        )
        self.tree.heading("date", text="Date")
        self.tree.heading("category", text="Category")
        self.tree.heading("amount", text="Amount")
        self.tree.heading("note", text="Note")

        self.tree.column("date", width=84, anchor="center")
        self.tree.column("category", width=92, anchor="w")
        self.tree.column("amount", width=72, anchor="e")
        self.tree.column("note", width=122, anchor="w")

        scrollbar = ttk.Scrollbar(
            tree_container, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 綁定雙擊事件開啟編輯視窗
        self.tree.bind("<Double-1>", self._on_tree_double_click)

        # 表格底部操作按鈕列
        action_bar = ttk.Frame(table_card, style="Card.TFrame")
        action_bar.pack(fill="x", pady=(8, 0))
        ttk.Button(
            action_bar,
            text="Edit Selected",
            style="Secondary.TButton",
            command=self.edit_selected,
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ttk.Button(
            action_bar,
            text="Delete Selected",
            style="Danger.TButton",
            command=self.delete_selected,
        ).pack(side="right", expand=True, fill="x")

        # === 右側：控制列 + 預算進度條 + 即時甜甜圈圖 ===
        right_panel = ttk.Frame(main_frame, style="Card.TFrame", padding=14)
        right_panel.pack(side="right", fill="both", expand=True)

        # 頂部控制列（月份篩選 + 主題按鈕 + 存檔）
        ctrl_bar = ttk.Frame(right_panel, style="Card.TFrame")
        ctrl_bar.pack(fill="x", pady=(0, 10))

        ttk.Label(ctrl_bar, text="Filter Month:", style="Field.TLabel").pack(
            side="left", padx=(0, 6)
        )
        self.month_combo = ttk.Combobox(
            ctrl_bar, textvariable=self.month_var, state="readonly", width=11
        )
        self.month_combo.pack(side="left", padx=(0, 14))
        self.month_combo.bind("<<ComboboxSelected>>", lambda e: self.draw_chart())

        ttk.Button(
            ctrl_bar,
            text="Modern",
            style="Secondary.TButton",
            command=lambda: self.set_theme("modern"),
        ).pack(side="left", padx=2)
        ttk.Button(
            ctrl_bar,
            text="Morandi",
            style="Secondary.TButton",
            command=lambda: self.set_theme("morandi"),
        ).pack(side="left", padx=2)
        ttk.Button(
            ctrl_bar,
            text="Dark",
            style="Secondary.TButton",
            command=lambda: self.set_theme("dark"),
        ).pack(side="left", padx=2)

        ttk.Button(
            ctrl_bar,
            text="Save PNG",
            style="Primary.TButton",
            command=self.save_png,
        ).pack(side="right")

        # 預算進度條區塊
        budget_frame = tk.Frame(
            right_panel,
            bg="#F8FAFC",
            highlightbackground="#E2E8F0",
            highlightthickness=1,
            padx=12,
            pady=8,
        )
        budget_frame.pack(fill="x", pady=(0, 10))

        budget_top = tk.Frame(budget_frame, bg="#F8FAFC")
        budget_top.pack(fill="x", pady=(0, 6))

        tk.Label(
            budget_top,
            text="Budget Limit ($):",
            bg="#F8FAFC",
            fg="#334155",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left")

        budget_entry = ttk.Entry(budget_top, textvariable=self.budget_var, width=9)
        budget_entry.pack(side="left", padx=(6, 6))
        budget_entry.bind("<Return>", lambda e: self.apply_budget())

        ttk.Button(
            budget_top,
            text="Set",
            style="Secondary.TButton",
            command=self.apply_budget,
        ).pack(side="left")

        self.budget_status_label = tk.Label(
            budget_top,
            textvariable=self.budget_status_var,
            bg="#F8FAFC",
            fg="#059669",
            font=("Segoe UI", 9, "bold"),
        )
        self.budget_status_label.pack(side="right")

        self.progress_bar = ttk.Progressbar(
            budget_frame,
            orient="horizontal",
            mode="determinate",
            maximum=100,
            style="Green.Horizontal.TProgressbar",
        )
        self.progress_bar.pack(fill="x")

        # 內嵌 Matplotlib 畫布
        self.fig = Figure(figsize=(7.2, 4.9), dpi=105)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_panel)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # === 資料驗證與讀寫 ===
    def _validate_fields(self, date_str, amount_str, category):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror(
                "Invalid Date", "Please use YYYY-MM-DD format (e.g., 2026-11-25)."
            )
            return None

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Amount", "Amount must be a positive number.")
            return None

        if not category:
            messagebox.showerror("Invalid Category", "Category cannot be empty.")
            return None

        return amount

    def _save_all_rows(self):
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(self.rows)

    def add_expense(self):
        date_str = self.date_var.get().strip()
        amount_str = self.amount_var.get().strip()
        category = self.category_var.get().strip().title()
        note = self.note_var.get().strip()

        amount = self._validate_fields(date_str, amount_str, category)
        if amount is None:
            return

        init_csv()
        with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writerow(
                {
                    "date": date_str,
                    "amount": f"{amount:.2f}",
                    "category": category,
                    "note": note,
                }
            )

        self.amount_var.set("")
        self.note_var.set("")
        self.refresh_all()

    # === 編輯與刪除功能 ===
    def _on_tree_double_click(self, event):
        if self.tree.identify_row(event.y):
            self.edit_selected()

    def edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Record", "Please select an expense row to edit.")
            return

        idx = int(selected[0])
        record = self.rows[idx]

        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Expense")
        dialog.geometry("340x240")
        dialog.resizable(False, False)
        dialog.configure(bg="#FFFFFF")
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ttk.Frame(dialog, style="Card.TFrame", padding=16)
        frame.pack(fill="both", expand=True)

        d_var = tk.StringVar(value=record["date"])
        a_var = tk.StringVar(value=record["amount"])
        c_var = tk.StringVar(value=record["category"])
        n_var = tk.StringVar(value=record.get("note", ""))

        ttk.Label(frame, text="Date (YYYY-MM-DD)", style="Field.TLabel").grid(
            row=0, column=0, sticky="w", pady=5
        )
        ttk.Entry(frame, textvariable=d_var, width=22).grid(
            row=0, column=1, sticky="ew", pady=5, padx=(10, 0)
        )

        ttk.Label(frame, text="Amount ($)", style="Field.TLabel").grid(
            row=1, column=0, sticky="w", pady=5
        )
        ttk.Entry(frame, textvariable=a_var, width=22).grid(
            row=1, column=1, sticky="ew", pady=5, padx=(10, 0)
        )

        ttk.Label(frame, text="Category", style="Field.TLabel").grid(
            row=2, column=0, sticky="w", pady=5
        )
        ttk.Combobox(frame, textvariable=c_var, values=CATEGORIES, width=20).grid(
            row=2, column=1, sticky="ew", pady=5, padx=(10, 0)
        )

        ttk.Label(frame, text="Note", style="Field.TLabel").grid(
            row=3, column=0, sticky="w", pady=5
        )
        ttk.Entry(frame, textvariable=n_var, width=22).grid(
            row=3, column=1, sticky="ew", pady=5, padx=(10, 0)
        )

        frame.columnconfigure(1, weight=1)

        def save_changes():
            new_date = d_var.get().strip()
            new_cat = c_var.get().strip().title()
            new_note = n_var.get().strip()
            new_amount = self._validate_fields(new_date, a_var.get().strip(), new_cat)
            if new_amount is None:
                return

            self.rows[idx] = {
                "date": new_date,
                "amount": f"{new_amount:.2f}",
                "category": new_cat,
                "note": new_note,
            }
            self._save_all_rows()
            dialog.destroy()
            self.refresh_all()

        btn_row = ttk.Frame(frame, style="Card.TFrame")
        btn_row.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        ttk.Button(
            btn_row, text="Cancel", style="Secondary.TButton", command=dialog.destroy
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ttk.Button(
            btn_row, text="Save Changes", style="Primary.TButton", command=save_changes
        ).pack(side="right", expand=True, fill="x")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Record", "Please select an expense row to delete.")
            return

        idx = int(selected[0])
        rec = self.rows[idx]
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete this expense?\n\n{rec['date']} | {rec['category']} | ${float(rec['amount']):,.2f}",
        )
        if confirm:
            self.rows.pop(idx)
            self._save_all_rows()
            self.refresh_all()

    # === 預算更新與畫面刷新 ===
    def apply_budget(self):
        try:
            val = float(self.budget_var.get().strip())
            if val <= 0:
                raise ValueError
            self.budget_limit = val
            self.draw_chart()
        except ValueError:
            messagebox.showerror("Invalid Budget", "Budget must be a positive number.")
            self.budget_var.set(f"{self.budget_limit:.0f}")

    def _update_budget_bar(self, total_spent):
        pct = (total_spent / self.budget_limit) * 100 if self.budget_limit > 0 else 0
        self.progress_bar["value"] = min(pct, 100)

        if pct > 100:
            self.progress_bar.configure(style="Red.Horizontal.TProgressbar")
            self.budget_status_label.configure(fg="#DC2626")
            self.budget_status_var.set(
                f"OVER BUDGET!  ${total_spent:,.2f} / ${self.budget_limit:,.2f} ({pct:.1f}%)"
            )
        elif pct >= 80:
            self.progress_bar.configure(style="Amber.Horizontal.TProgressbar")
            self.budget_status_label.configure(fg="#D97706")
            self.budget_status_var.set(
                f"Warning:  ${total_spent:,.2f} / ${self.budget_limit:,.2f} ({pct:.1f}%)"
            )
        else:
            self.progress_bar.configure(style="Green.Horizontal.TProgressbar")
            self.budget_status_label.configure(fg="#059669")
            self.budget_status_var.set(
                f"${total_spent:,.2f} / ${self.budget_limit:,.2f} ({pct:.1f}%)"
            )

    def refresh_all(self):
        self._load_table_and_months()
        self.draw_chart()

    def _load_table_and_months(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.rows = []
        months = set()
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, mode="r", encoding="utf-8") as f:
                self.rows = list(csv.DictReader(f))

        # 反向顯示讓最新紀錄在最上方，同時用原始索引當 iid 確保編輯/刪除對應正確
        for idx in range(len(self.rows) - 1, -1, -1):
            row = self.rows[idx]
            date_val = row.get("date", "").strip()
            if len(date_val) >= 7:
                months.add(date_val[:7])
            self.tree.insert(
                "",
                "end",
                iid=str(idx),
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
        total_spent = sum(totals.values())
        self._update_budget_bar(total_spent)

        theme = THEMES[self.current_theme]
        self.fig.clear()
        self.fig.patch.set_facecolor(theme["bg"])

        if not totals:
            ax = self.fig.add_subplot(111)
            ax.set_facecolor(theme["bg"])
            ax.axis("off")
            ax.text(
                0.5,
                0.5,
                "No expenses recorded for this period.",
                ha="center",
                va="center",
                fontsize=12,
                color=theme["text"],
            )
            self.canvas.draw()
            return

        sorted_items = sorted(totals.items(), key=lambda x: x[1], reverse=True)
        categories = [item[0] for item in sorted_items]
        amounts = [item[1] for item in sorted_items]
        explode = [0.05 if i == 0 else 0 for i in range(len(amounts))]
        colors = [theme["colors"][i % len(theme["colors"])] for i in range(len(amounts))]

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
            0,
            0,
            f"Total Spent\n${total_spent:,.2f}",
            ha="center",
            va="center",
            fontsize=12,
            fontweight="bold",
            color=theme["text"],
        )

        legend_labels = [
            f"{cat:<13} ${amt:>8,.2f} ({amt / total_spent * 100:>5.1f}%)"
            for cat, amt in zip(categories, amounts)
        ]
        legend = ax.legend(
            wedges,
            legend_labels,
            title="Category Breakdown",
            title_fontsize=10,
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
            fontsize=14,
            fontweight="bold",
            color=theme["title"],
            pad=14,
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