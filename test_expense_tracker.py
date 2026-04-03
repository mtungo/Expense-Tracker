"""Tests for the expense tracker application."""

import json
import os
import tempfile

import pytest

from expense_tracker import (
    Expense,
    ExpenseTracker,
    InputValidator,
    JsonFileStorage,
    TableFormatter,
    CURRENCY_SYMBOL,
)


# --- Expense dataclass tests ---

class TestExpense:
    def test_create_new(self):
        expense = Expense.create_new(25.50, "Food", "Lunch")
        assert expense.amount == 25.50
        assert expense.category == "Food"
        assert expense.description == "Lunch"
        assert expense.expense_id  # non-empty
        assert expense.date  # non-empty

    def test_to_dict(self):
        expense = Expense("abc-123", 10.0, "Transport", "Bus", "2026-01-01 12:00:00")
        result = expense.to_dict()
        assert result == {
            "id": "abc-123",
            "amount": 10.0,
            "category": "Transport",
            "description": "Bus",
            "date": "2026-01-01 12:00:00",
        }

    def test_from_dict(self):
        data = {
            "id": "abc-123",
            "amount": 10.0,
            "category": "Transport",
            "description": "Bus",
            "date": "2026-01-01 12:00:00",
        }
        expense = Expense.from_dict(data)
        assert expense.expense_id == "abc-123"
        assert expense.amount == 10.0

    def test_from_dict_converts_int_id_to_str(self):
        data = {
            "id": 42,
            "amount": 5.0,
            "category": "Misc",
            "description": "Test",
            "date": "2026-01-01 12:00:00",
        }
        expense = Expense.from_dict(data)
        assert expense.expense_id == "42"
        assert isinstance(expense.expense_id, str)

    def test_roundtrip_dict(self):
        original = Expense.create_new(99.99, "Entertainment", "Movie")
        restored = Expense.from_dict(original.to_dict())
        assert restored.expense_id == original.expense_id
        assert restored.amount == original.amount
        assert restored.category == original.category
        assert restored.description == original.description
        assert restored.date == original.date


# --- InputValidator tests ---

class TestInputValidator:
    def test_validate_amount_positive(self):
        assert InputValidator.validate_amount(10.0) is True

    def test_validate_amount_zero(self):
        assert InputValidator.validate_amount(0) is False

    def test_validate_amount_negative(self):
        assert InputValidator.validate_amount(-5.0) is False

    def test_validate_text_field_valid(self):
        assert InputValidator.validate_text_field("Hello") is True

    def test_validate_text_field_empty(self):
        assert InputValidator.validate_text_field("") is False

    def test_validate_text_field_whitespace_only(self):
        assert InputValidator.validate_text_field("   ") is False

    def test_validate_text_field_too_long(self):
        assert InputValidator.validate_text_field("x" * 101) is False

    def test_validate_text_field_max_length(self):
        assert InputValidator.validate_text_field("x" * 100) is True

    def test_validate_choice_in_range(self):
        assert InputValidator.validate_choice(3, 1, 5) is True

    def test_validate_choice_at_bounds(self):
        assert InputValidator.validate_choice(1, 1, 5) is True
        assert InputValidator.validate_choice(5, 1, 5) is True

    def test_validate_choice_out_of_range(self):
        assert InputValidator.validate_choice(0, 1, 5) is False
        assert InputValidator.validate_choice(6, 1, 5) is False


# --- JsonFileStorage tests ---

class TestJsonFileStorage:
    def test_save_and_load(self, tmp_path):
        filepath = str(tmp_path / "test_expenses.json")
        storage = JsonFileStorage(filepath)
        expenses = [
            Expense.create_new(10.0, "Food", "Lunch"),
            Expense.create_new(20.0, "Transport", "Taxi"),
        ]
        storage.save_expenses(expenses)
        loaded = storage.load_expenses()

        assert len(loaded) == 2
        assert loaded[0].amount == 10.0
        assert loaded[1].category == "Transport"

    def test_load_nonexistent_file(self, tmp_path):
        filepath = str(tmp_path / "nonexistent.json")
        storage = JsonFileStorage(filepath)
        assert storage.load_expenses() == []

    def test_load_corrupted_json(self, tmp_path):
        filepath = str(tmp_path / "bad.json")
        with open(filepath, "w") as f:
            f.write("not valid json{{{")
        storage = JsonFileStorage(filepath)
        assert storage.load_expenses() == []

    def test_load_missing_keys(self, tmp_path):
        filepath = str(tmp_path / "incomplete.json")
        with open(filepath, "w") as f:
            json.dump([{"id": "1", "amount": 5.0}], f)
        storage = JsonFileStorage(filepath)
        assert storage.load_expenses() == []


# --- ExpenseTracker tests ---

class TestExpenseTracker:
    @pytest.fixture
    def tracker(self, tmp_path):
        filepath = str(tmp_path / "test_expenses.json")
        storage = JsonFileStorage(filepath)
        return ExpenseTracker(storage)

    def test_add_expense(self, tracker):
        expense = tracker.add_expense(15.0, "Food", "Lunch")
        assert expense is not None
        assert expense.amount == 15.0
        assert len(tracker.get_all_expenses()) == 1

    def test_add_expense_invalid_amount(self, tracker):
        assert tracker.add_expense(-5.0, "Food", "Lunch") is None
        assert len(tracker.get_all_expenses()) == 0

    def test_add_expense_empty_category(self, tracker):
        assert tracker.add_expense(10.0, "", "Lunch") is None

    def test_add_expense_empty_description(self, tracker):
        assert tracker.add_expense(10.0, "Food", "") is None

    def test_add_expense_strips_whitespace(self, tracker):
        expense = tracker.add_expense(10.0, "  Food  ", "  Lunch  ")
        assert expense.category == "Food"
        assert expense.description == "Lunch"

    def test_calculate_total_spending(self, tracker):
        tracker.add_expense(10.0, "Food", "Lunch")
        tracker.add_expense(20.0, "Transport", "Taxi")
        assert tracker.calculate_total_spending() == 30.0

    def test_calculate_total_spending_empty(self, tracker):
        assert tracker.calculate_total_spending() == 0.0

    def test_get_spending_by_category(self, tracker):
        tracker.add_expense(10.0, "Food", "Lunch")
        tracker.add_expense(5.0, "Food", "Snack")
        tracker.add_expense(20.0, "Transport", "Taxi")
        result = tracker.get_spending_by_category()
        assert result == {"Food": 15.0, "Transport": 20.0}

    def test_filter_by_category(self, tracker):
        tracker.add_expense(10.0, "Food", "Lunch")
        tracker.add_expense(20.0, "Transport", "Taxi")
        tracker.add_expense(5.0, "food", "Snack")  # different case

        filtered = tracker.filter_by_category("Food")
        assert len(filtered) == 2

    def test_filter_by_category_no_match(self, tracker):
        tracker.add_expense(10.0, "Food", "Lunch")
        assert tracker.filter_by_category("Transport") == []

    def test_get_available_categories(self, tracker):
        tracker.add_expense(10.0, "Food", "Lunch")
        tracker.add_expense(20.0, "Transport", "Taxi")
        tracker.add_expense(5.0, "Food", "Snack")
        categories = tracker.get_available_categories()
        assert categories == ["Food", "Transport"]

    def test_get_available_categories_empty(self, tracker):
        assert tracker.get_available_categories() == []

    def test_persistence(self, tmp_path):
        filepath = str(tmp_path / "test_expenses.json")
        storage = JsonFileStorage(filepath)
        tracker1 = ExpenseTracker(storage)
        tracker1.add_expense(10.0, "Food", "Lunch")

        tracker2 = ExpenseTracker(JsonFileStorage(filepath))
        assert len(tracker2.get_all_expenses()) == 1
        assert tracker2.get_all_expenses()[0].amount == 10.0

    def test_get_all_expenses_returns_copy(self, tracker):
        tracker.add_expense(10.0, "Food", "Lunch")
        expenses = tracker.get_all_expenses()
        expenses.clear()
        assert len(tracker.get_all_expenses()) == 1


# --- TableFormatter tests ---

class TestTableFormatter:
    def test_print_expenses_table_empty(self, capsys):
        TableFormatter.print_expenses_table([])
        assert "No expenses recorded." in capsys.readouterr().out

    def test_print_expenses_table(self, capsys):
        expenses = [Expense("abc", 10.0, "Food", "Lunch", "2026-01-01 12:00:00")]
        TableFormatter.print_expenses_table(expenses)
        output = capsys.readouterr().out
        assert "abc" in output
        assert "Food" in output
        assert "10.00" in output

    def test_print_category_breakdown(self, capsys):
        TableFormatter.print_category_breakdown({"Food": 30.0, "Transport": 20.0})
        output = capsys.readouterr().out
        assert "Food" in output
        assert "Transport" in output
        assert "60.0%" in output
        assert "40.0%" in output

    def test_print_category_expenses_empty(self, capsys):
        TableFormatter.print_category_expenses([], "Food")
        assert "No expenses found" in capsys.readouterr().out

    def test_print_category_expenses(self, capsys):
        expenses = [Expense("abc", 10.0, "Food", "Lunch", "2026-01-01 12:00:00")]
        TableFormatter.print_category_expenses(expenses, "Food")
        output = capsys.readouterr().out
        assert "Food" in output
        assert "10.00" in output
