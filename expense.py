import json
import os
from datetime import datetime


DATA_FILE = "expenses.json"


def load_expenses():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_expenses(expenses):
    with open(DATA_FILE, "w") as f:
        json.dump(expenses, f, indent=2)


def add_expense(amount, category, description):
    expenses = load_expenses()
    expense = {
        "id": len(expenses) + 1,
        "amount": round(float(amount), 2),
        "category": category,
        "description": description,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    expenses.append(expense)
    save_expenses(expenses)
    return expense


def get_all_expenses():
    return load_expenses()


def get_total_spending():
    expenses = load_expenses()
    return round(sum(e["amount"] for e in expenses), 2)


def get_spending_by_category():
    expenses = load_expenses()
    totals = {}
    for e in expenses:
        totals[e["category"]] = totals.get(e["category"], 0) + e["amount"]
    return {k: round(v, 2) for k, v in totals.items()}
