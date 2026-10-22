"""
Student Finance Manager
A multi-view Flet application for tracking student income, expenses, budgets, and savings.
Requires Flet 1.x:  pip install -U flet
Run with: python main.py
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any
from uuid import uuid4

import flet as ft

APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / "finance_data.json"


@dataclass
class Transaction:
    id: str
    kind: str                 # "Income" or "Expense"
    title: str
    category: str
    amount: float
    transaction_date: str
    note: str = ""


@dataclass
class Budget:
    category: str
    limit: float


@dataclass
class SavingsGoal:
    title: str
    target: float
    saved: float = 0.0


class FinanceStore:
    """Loads and saves app data in a local JSON file."""

    def __init__(self, path: Path = DATA_FILE):
        self.path = Path(path)
        self.transactions: list[Transaction] = []
        self.budgets: list[Budget] = []
        self.goals: list[SavingsGoal] = []
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self.save()
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self.transactions = [Transaction(**i) for i in data.get("transactions", [])]
            self.budgets = [Budget(**i) for i in data.get("budgets", [])]
            self.goals = [SavingsGoal(**i) for i in data.get("goals", [])]
        except (json.JSONDecodeError, TypeError, ValueError):
            self.transactions, self.budgets, self.goals = [], [], []

    def save(self) -> None:
        payload = {
            "transactions": [asdict(i) for i in self.transactions],
            "budgets": [asdict(i) for i in self.budgets],
            "goals": [asdict(i) for i in self.goals],
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @property
    def income(self) -> float:
        return sum(t.amount for t in self.transactions if t.kind == "Income")

    @property
    def expenses(self) -> float:
        return sum(t.amount for t in self.transactions if t.kind == "Expense")

    @property
    def balance(self) -> float:
        return self.income - self.expenses

    def add_transaction(self, kind: str, title: str, category: str, amount: float,
                        transaction_date: str, note: str = "") -> None:
        if kind not in {"Income", "Expense"}:
            raise ValueError("Transaction type must be Income or Expense.")
        if not title.strip() or not category.strip():
            raise ValueError("Title and category are required.")
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        date.fromisoformat(transaction_date)
        self.transactions.insert(0, Transaction(
            id=str(uuid4()), kind=kind, title=title.strip(), category=category.strip(),
            amount=round(amount, 2), transaction_date=transaction_date, note=note.strip()
        ))
        self.save()

    def delete_transaction(self, transaction_id: str) -> None:
        self.transactions = [t for t in self.transactions if t.id != transaction_id]
        self.save()

    def set_budget(self, category: str, limit: float) -> None:
        if not category.strip() or limit <= 0:
            raise ValueError("Enter a category and a budget greater than zero.")
        existing = next((b for b in self.budgets if b.category.lower() == category.strip().lower()), None)
        if existing:
            existing.limit = round(limit, 2)
        else:
            self.budgets.append(Budget(category=category.strip(), limit=round(limit, 2)))
        self.save()

    def add_goal(self, title: str, target: float, saved: float = 0.0) -> None:
        if not title.strip() or target <= 0 or saved < 0:
            raise ValueError("Enter a goal title, a positive target, and a non-negative saved amount.")
        self.goals.append(SavingsGoal(title=title.strip(), target=round(target, 2), saved=round(saved, 2)))
        self.save()

    def update_goal_saved(self, title: str, saved: float) -> None:
        if saved < 0:
            raise ValueError("Saved amount cannot be negative.")
        goal = next((g for g in self.goals if g.title == title), None)
        if not goal:
            raise ValueError("Savings goal not found.")
        goal.saved = round(saved, 2)
        self.save()


def bp(**breakpoints: int) -> Any:
    """Responsive column spans, e.g. bp(sm=12, md=6)."""
    return breakpoints


def money(value: float) -> str:
    return f"N$ {value:,.2f}"


def to_float(text: str | None, default: str = "") -> float:
    return float((text or default).replace(",", "").strip())


def main(page: ft.Page):
    store = FinanceStore()
    page.title = "Student Finance Manager"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = "#F4F7FB"
    page.window.width = 1180
    page.window.height = 820
    page.window.min_width = 360
    page.window.min_height = 600

    NAVY = "#14213D"
    TEAL = "#0F9D8A"
    MUTED = "#64748B"
    CARD = "#FFFFFF"
    BORDER = "#E2E8F0"
    RED = "#D94841"

    current_view = {"name": "Dashboard"}
    content = ft.Column(expand=True, spacing=18, scroll=ft.ScrollMode.AUTO)
    nav_buttons: dict[str, ft.Container] = {}
    status = ft.Text("", color=TEAL, size=13)

    def notify(message: str, error: bool = False):
        status.value = message
        status.color = "#B42318" if error else TEAL
        page.show_dialog(ft.SnackBar(content=ft.Text(message)))

    def card(title: str, value: str, subtitle: str, icon: ft.IconData, accent: str):
        return ft.Container(
            expand=True, padding=18, bgcolor=CARD, border=ft.Border.all(1, BORDER),
            border_radius=16,
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        width=42, height=42, border_radius=12,
                        bgcolor=accent + "20",
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(icon=icon, color=accent, size=22),
                    ),
                    ft.Container(expand=True, content=ft.Text(title, color=MUTED, size=13, weight=ft.FontWeight.W_500)),
                ]),
                ft.Text(value, size=25, weight=ft.FontWeight.BOLD, color=NAVY),
                ft.Text(subtitle, size=12, color=MUTED),
            ], spacing=10)
        )

    def section_title(title: str, subtitle: str):
        return ft.Column([
            ft.Text(title, size=26, weight=ft.FontWeight.BOLD, color=NAVY),
            ft.Text(subtitle, size=13, color=MUTED),
        ], spacing=4)

    def make_button(label: str, icon: ft.IconData, on_click, primary=False):
        return ft.FilledButton(
            content=label, icon=icon, on_click=on_click,
            bgcolor=TEAL if primary else "#E8EEF5",
            color="#FFFFFF" if primary else NAVY,
            style=ft.ButtonStyle(padding=ft.Padding.symmetric(horizontal=16, vertical=14)),
        )

    def show_view(name: str):
        current_view["name"] = name
        for key, btn in nav_buttons.items():
            btn.bgcolor = "#23365D" if key == name else None
            if isinstance(btn.content, ft.Row) and len(btn.content.controls) > 1:
                label = btn.content.controls[1]
                if isinstance(label, ft.Text):
                    label.color = "#FFFFFF" if key == name else "#CBD5E1"
        render()

    def nav_item(name: str, icon: ft.IconData):
        btn = ft.Container(
            padding=ft.Padding.symmetric(horizontal=14, vertical=12),
            border_radius=10,
            ink=True,
            on_click=lambda e, n=name: show_view(n),
            content=ft.Row([
                ft.Icon(icon, color="#CBD5E1", size=20),
                ft.Text(name, color="#CBD5E1", size=14, weight=ft.FontWeight.W_500),
            ], spacing=12),
        )
        nav_buttons[name] = btn
        return btn

    # ------------------------------------------------------------------ views
    def dashboard_view():
        recent_rows = []
        for t in store.transactions[:5]:
            is_income = t.kind == "Income"
            recent_rows.append(ft.Container(
                padding=ft.Padding.symmetric(vertical=10),
                border=ft.Border.only(bottom=ft.BorderSide(1, BORDER)),
                content=ft.Row([
                    ft.Container(
                        width=38, height=38, border_radius=11,
                        bgcolor="#E7F7F3" if is_income else "#FFF0ED",
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(ft.Icons.SOUTH_WEST if is_income else ft.Icons.NORTH_EAST,
                                        color=TEAL if is_income else RED, size=18),
                    ),
                    ft.Column([
                        ft.Text(t.title, weight=ft.FontWeight.W_600, color=NAVY),
                        ft.Text(f"{t.category} • {t.transaction_date}", size=12, color=MUTED),
                    ], expand=True, spacing=3),
                    ft.Text(("+" if is_income else "−") + money(t.amount),
                            color=TEAL if is_income else RED, weight=ft.FontWeight.BOLD),
                ])
            ))
        if not recent_rows:
            recent_rows = [ft.Text("No transactions yet. Add your first income or expense.", color=MUTED)]

        cardcol = bp(sm=12, md=6, lg=3)
        return [
            section_title("Your money, made clearer.", "A simple overview of your student finances."),
            ft.ResponsiveRow([
                ft.Container(content=card("Current balance", money(store.balance), "Income minus expenses", ft.Icons.ACCOUNT_BALANCE_WALLET, TEAL), col=cardcol),
                ft.Container(content=card("Total income", money(store.income), "All recorded income", ft.Icons.TRENDING_UP, "#238636"), col=cardcol),
                ft.Container(content=card("Total expenses", money(store.expenses), "All recorded spending", ft.Icons.TRENDING_DOWN, RED), col=cardcol),
                ft.Container(content=card("Savings goals", str(len(store.goals)), "Goals you're working toward", ft.Icons.SAVINGS, "#7C5CFC"), col=cardcol),
            ], spacing=12, run_spacing=12),
            ft.Container(
                padding=20, bgcolor=CARD, border=ft.Border.all(1, BORDER), border_radius=16,
                content=ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text("Recent transactions", size=18, weight=ft.FontWeight.BOLD, color=NAVY),
                            ft.Text("Your latest recorded activity", color=MUTED, size=12),
                        ], expand=True),
                        make_button("View all", ft.Icons.ARROW_FORWARD, lambda e: show_view("Transactions")),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Column(controls=list(recent_rows), spacing=0),
                ], spacing=14)
            ),
            ft.Container(
                padding=20, bgcolor="#E8F7F4", border_radius=16,
                content=ft.Row([
                    ft.Icon(ft.Icons.LIGHTBULB_OUTLINE, color=TEAL, size=26),
                    ft.Column([
                        ft.Text("Small steps count", color=NAVY, weight=ft.FontWeight.BOLD),
                        ft.Text("Record spending regularly to understand where your money goes.", color="#37665F", size=13),
                    ], expand=True),
                ], spacing=14)
            ),
        ]

    def delete_tx(transaction_id: str):
        store.delete_transaction(transaction_id)
        notify("Transaction deleted.")
        render()

    def transactions_view():
        kind = ft.Dropdown(label="Type", value="Expense", width=150, border_radius=10,
                           options=[ft.DropdownOption("Expense"), ft.DropdownOption("Income")])
        title = ft.TextField(label="Description", hint_text="e.g. Groceries or holiday job", expand=True, border_radius=10)
        category = ft.Dropdown(
            label="Category", value="Food", width=190, border_radius=10,
            options=[ft.DropdownOption(x) for x in
                     ["Food", "Transport", "Accommodation", "Study", "Data & airtime",
                      "Personal care", "Salary / job", "Allowance", "Other"]])
        amount = ft.TextField(label="Amount (N$)", keyboard_type=ft.KeyboardType.NUMBER, width=160, border_radius=10)
        trans_date = ft.TextField(label="Date (YYYY-MM-DD)", value=date.today().isoformat(), width=190, border_radius=10)
        note = ft.TextField(label="Note (optional)", hint_text="Add a short note", expand=True, border_radius=10)

        def add(e):
            try:
                store.add_transaction(kind.value or "Expense", title.value or "", category.value or "Other",
                                      to_float(amount.value), (trans_date.value or "").strip(), note.value or "")
                notify("Transaction added successfully.")
                render()
            except (ValueError, TypeError) as ex:
                notify(str(ex) or "Please check the details and try again.", True)

        rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(t.transaction_date)),
                ft.DataCell(ft.Text(t.title)),
                ft.DataCell(ft.Text(t.category)),
                ft.DataCell(ft.Text(t.kind)),
                ft.DataCell(ft.Text(money(t.amount))),
                ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, tooltip="Delete transaction",
                                          on_click=lambda e, tid=t.id: delete_tx(tid))),
            ]) for t in store.transactions
        ]
        table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(x)) for x in ["Date", "Description", "Category", "Type", "Amount", ""]], # pyright: ignore[reportCallIssue]
            rows=rows, column_spacing=18, heading_row_height=44, data_row_min_height=48,
        )
        return [
            section_title("Transactions", "Add and manage your income and expenses."),
            ft.Container(
                padding=20, bgcolor=CARD, border=ft.Border.all(1, BORDER), border_radius=16,
                content=ft.Column([
                    ft.Text("Add a transaction", size=18, weight=ft.FontWeight.BOLD, color=NAVY),
                    ft.ResponsiveRow([
                        ft.Container(content=kind, col=bp(sm=6, md=2)),
                        ft.Container(content=title, col=bp(sm=12, md=4)),
                        ft.Container(content=category, col=bp(sm=12, md=3)),
                        ft.Container(content=amount, col=bp(sm=6, md=3)),
                        ft.Container(content=trans_date, col=bp(sm=12, md=4)),
                        ft.Container(content=note, col=bp(sm=12, md=5)),
                        ft.Container(content=make_button("Add transaction", ft.Icons.ADD, add, True), col=bp(sm=12, md=3)),
                    ], spacing=10, run_spacing=10),
                ], spacing=14)
            ),
            ft.Container(
                padding=16, bgcolor=CARD, border=ft.Border.all(1, BORDER), border_radius=16,
                content=ft.Column([
                    ft.Text("Transaction history", size=18, weight=ft.FontWeight.BOLD, color=NAVY),
                    ft.Row([table], scroll=ft.ScrollMode.AUTO) if rows else ft.Text("No transactions yet.", color=MUTED),
                ], spacing=12)
            ),
        ]

    def budgets_view():
        budget_category = ft.TextField(label="Category", hint_text="e.g. Food", expand=True, border_radius=10)
        budget_limit = ft.TextField(label="Monthly limit (N$)", keyboard_type=ft.KeyboardType.NUMBER, width=220, border_radius=10)

        def save_budget(e):
            try:
                store.set_budget(budget_category.value or "", to_float(budget_limit.value))
                notify("Budget saved.")
                render()
            except (ValueError, TypeError) as ex:
                notify(str(ex) or "Enter a valid budget.", True)

        spent_by_category: dict[str, float] = {}
        for t in store.transactions:
            if t.kind == "Expense":
                k = t.category.lower()
                spent_by_category[k] = spent_by_category.get(k, 0) + t.amount

        budget_cards: list[ft.Control] = []
        for b in store.budgets:
            spent = spent_by_category.get(b.category.lower(), 0)
            ratio = min(spent / b.limit, 1.0) if b.limit else 0
            over = spent > b.limit
            budget_cards.append(ft.Container(
                padding=16, border=ft.Border.all(1, BORDER), border_radius=14, bgcolor="#FFFFFF",
                content=ft.Column([
                    ft.Row([
                        ft.Text(b.category, weight=ft.FontWeight.BOLD, color=NAVY, size=16),
                        ft.Container(expand=True),
                        ft.Text(f"{money(spent)} / {money(b.limit)}", color=RED if over else MUTED, size=12),
                    ]),
                    ft.ProgressBar(value=ratio, color=RED if over else TEAL, bgcolor="#E8EEF5", bar_height=8),
                    ft.Text("Over budget" if over else f"{money(max(b.limit - spent, 0))} remaining",
                            color=RED if over else MUTED, size=12),
                ], spacing=10)
            ))
        if not budget_cards:
            budget_cards = [ft.Text("No budgets set yet. Add a category and monthly limit above.", color=MUTED)]

        return [
            section_title("Budgets", "Set spending limits and see how much you've used."),
            ft.Container(
                padding=20, bgcolor=CARD, border=ft.Border.all(1, BORDER), border_radius=16,
                content=ft.Column([
                    ft.Text("Create or update a budget", size=18, weight=ft.FontWeight.BOLD, color=NAVY),
                    ft.ResponsiveRow([
                        ft.Container(content=budget_category, col=bp(sm=12, md=5)),
                        ft.Container(content=budget_limit, col=bp(sm=12, md=4)),
                        ft.Container(content=make_button("Save budget", ft.Icons.SAVINGS, save_budget, True), col=bp(sm=12, md=3)),
                    ], spacing=10, run_spacing=10),
                ], spacing=14)
            ),
            ft.Column(budget_cards, spacing=12),
        ]

    def savings_view():
        goal_title = ft.TextField(label="Goal name", hint_text="e.g. New laptop", expand=True, border_radius=10)
        target = ft.TextField(label="Target (N$)", keyboard_type=ft.KeyboardType.NUMBER, width=180, border_radius=10)
        saved = ft.TextField(label="Already saved (N$)", value="0", keyboard_type=ft.KeyboardType.NUMBER, width=200, border_radius=10)
        goal_fields: dict[str, ft.TextField] = {}

        def create_goal(e):
            try:
                store.add_goal(goal_title.value or "", to_float(target.value), to_float(saved.value, "0"))
                notify("Savings goal created.")
                render()
            except (ValueError, TypeError) as ex:
                notify(str(ex) or "Please check the goal details.", True)

        def update_goal(title: str):
            field = goal_fields.get(title)
            if field is None:
                notify("Could not find the savings amount field. Please try again.", True)
                return
            try:
                store.update_goal_saved(title, to_float(field.value))
                notify("Savings progress updated.")
                render()
            except (ValueError, TypeError) as ex:
                notify(str(ex) or "Enter a valid amount.", True)

        goal_cards = []
        for g in store.goals:
            progress = min(g.saved / g.target, 1.0) if g.target else 0
            saved_field = ft.TextField(label="Update saved amount", value=f"{g.saved:.2f}",
                                       keyboard_type=ft.KeyboardType.NUMBER, width=220, border_radius=10)
            goal_fields[g.title] = saved_field
            goal_cards.append(ft.Container(
                padding=18, bgcolor=CARD, border=ft.Border.all(1, BORDER), border_radius=16,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.SAVINGS, color="#7C5CFC", size=24),
                        ft.Text(g.title, size=17, weight=ft.FontWeight.BOLD, color=NAVY, expand=True),
                        ft.Text(f"{progress * 100:.0f}%", color=TEAL, weight=ft.FontWeight.BOLD),
                    ]),
                    ft.ProgressBar(value=progress, color="#7C5CFC", bgcolor="#E8EEF5", bar_height=9),
                    ft.Text(f"{money(g.saved)} saved of {money(g.target)} • {money(max(g.target - g.saved, 0))} to go",
                            color=MUTED, size=12),
                    ft.Row([saved_field,
                            make_button("Update progress", ft.Icons.CHECK,
                                        lambda e, title=g.title: update_goal(title), True)], wrap=True),
                ], spacing=12)
            ))
        if not goal_cards:
            goal_cards = [ft.Text("No savings goals yet. Create one to track your progress.", color=MUTED)]

        return [
            section_title("Savings goals", "Turn your plans into trackable milestones."),
            ft.Container(
                padding=20, bgcolor=CARD, border=ft.Border.all(1, BORDER), border_radius=16,
                content=ft.Column([
                    ft.Text("Create a savings goal", size=18, weight=ft.FontWeight.BOLD, color=NAVY),
                    ft.ResponsiveRow([
                        ft.Container(content=goal_title, col=bp(sm=12, md=5)),
                        ft.Container(content=target, col=bp(sm=12, md=3)),
                        ft.Container(content=saved, col=bp(sm=12, md=2)),
                        ft.Container(content=make_button("Create goal", ft.Icons.ADD, create_goal, True), col=bp(sm=12, md=2)),
                    ], spacing=10, run_spacing=10),
                ], spacing=14)
            ),
            ft.Column(goal_cards, spacing=12), # type: ignore
        ]

    def about_view():
        return [
            section_title("About this project", "A capstone application demonstrating the complete software lifecycle."),
            ft.Container(
                padding=24, bgcolor=CARD, border=ft.Border.all(1, BORDER), border_radius=16,
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, color=TEAL, size=34),
                            ft.Text("Student Finance Manager", size=22, weight=ft.FontWeight.BOLD, color=NAVY)]),
                    ft.Text("A student-focused finance tracker built with Python, object-oriented data models, JSON persistence, and a multi-view Flet interface.", color=MUTED),
                    ft.Divider(color=BORDER),
                    ft.Text("Key features", weight=ft.FontWeight.BOLD, color=NAVY),
                    ft.Text("• Dashboard summary for balance, income, expenses, and savings goals"),
                    ft.Text("• Add and delete income and expense transactions"),
                    ft.Text("• Create budgets and monitor spending against limits"),
                    ft.Text("• Create savings goals and update progress"),
                    ft.Text("• Persist data between application sessions using a local JSON file"),
                    ft.Divider(color=BORDER),
                    ft.Text("Important: this is a learning project. Data is stored locally on the device where the app runs. It is not a bank connection and should not be used to store passwords or banking credentials.", size=12, color=MUTED),
                ], spacing=12)
            ),
        ] 

    views = {
        "Dashboard": dashboard_view,
        "Transactions": transactions_view,
        "Budgets": budgets_view,
        "Savings goals": savings_view,
        "About project": about_view,
    }

    def render():
        content.controls = views[current_view["name"]]()
        page.update()

    # ---------------------------------------------------------------- layout
    sidebar = ft.Container(
        width=238, bgcolor=NAVY, padding=18,
        content=ft.Column([
            ft.Row([
                ft.Container(width=42, height=42, border_radius=13, bgcolor=TEAL,
                             alignment=ft.Alignment.CENTER,
                             content=ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, color="#FFFFFF", size=24)),
                ft.Column([
                    ft.Text("STUDENT", color="#FFFFFF", weight=ft.FontWeight.BOLD, size=13),
                    ft.Text("FINANCE MANAGER", color="#AFC4D8", size=10, weight=ft.FontWeight.W_600),
                ], spacing=2),
            ], spacing=10),
            ft.Container(height=22),
            ft.Text("WORKSPACE", color="#8295B2", size=10, weight=ft.FontWeight.BOLD),
            nav_item("Dashboard", ft.Icons.DASHBOARD_OUTLINED),
            nav_item("Transactions", ft.Icons.RECEIPT_LONG),
            nav_item("Budgets", ft.Icons.PIE_CHART_OUTLINE),
            nav_item("Savings goals", ft.Icons.SAVINGS),
            ft.Container(expand=True),
            ft.Divider(color="#344765"),
            nav_item("About project", ft.Icons.INFO_OUTLINE),
            ft.Text("CAPSTONE • 2026", color="#8295B2", size=10),
        ], spacing=7, expand=True)
    )

    header = ft.Container(
        padding=ft.Padding.symmetric(horizontal=24, vertical=16),
        bgcolor="#FFFFFF",
        border=ft.Border.only(bottom=ft.BorderSide(1, BORDER)),
        content=ft.Row([
            ft.Column([
                ft.Text("Personal finance workspace", color=NAVY, weight=ft.FontWeight.BOLD, size=16),
                ft.Text("Plan smarter. Spend consciously. Save consistently.", color=MUTED, size=11),
            ], expand=True, spacing=3),
            ft.Container(
                padding=ft.Padding.symmetric(horizontal=12, vertical=8), bgcolor="#E8F7F4", border_radius=20,
                content=ft.Row([ft.Icon(ft.Icons.CIRCLE, color=TEAL, size=8),
                                ft.Text("Local data saved", color="#167568", size=11)], spacing=6)
            )
        ])
    )

    page.add(
        ft.Row([
            sidebar,
            ft.Column([header, ft.Container(content=content, padding=24, expand=True), status],
                      expand=True, spacing=0),
        ], expand=True, spacing=0)
    )
    show_view("Dashboard")


if __name__ == "__main__":
    ft.run(main)
