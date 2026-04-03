"""Shared dependencies for API routes."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from expense_tracker import ExpenseTracker, JsonFileStorage

_storage = JsonFileStorage(os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "expenses.json"
))
_tracker = ExpenseTracker(_storage)


def get_tracker() -> ExpenseTracker:
    """Get the shared ExpenseTracker instance."""
    return _tracker
