# Expense Tracker

A command-line expense tracker that lets you record, view, and analyse personal spending. Data is stored locally in a JSON file.

## Requirements

- Python 3.7+

No external dependencies required — uses only the Python standard library.

## Usage

```bash
python expense_tracker.py
```

This launches an interactive menu:

```
Welcome to the Expense Tracker!

Select an option:
1. Add expense
2. View all expenses
3. Calculate total spending
4. View spending by category
5. Filter expenses by category
6. Quit
```

### Adding an Expense

Select option `1` and enter the amount, category, and description when prompted:

```
Enter amount: £12.50
Enter category: food
Enter description: Lunch at cafe
Expense added: £12.50 for food
```

### Viewing Expenses

Select option `2` to see all recorded expenses in a formatted table:

```
================================================================================
ID       Date                 Category        Amount     Description
================================================================================
a1b2c3d4 2026-04-02 10:30:00  food            £12.50     Lunch at cafe
e5f6a7b8 2026-04-02 14:00:00  transport       £3.25      Bus fare
================================================================================
```

### Spending Summary

- Option `3` — calculate total spending across all categories
- Option `4` — view spending broken down by category with percentages
- Option `5` — filter and view expenses for a specific category

## Data Storage

Expenses are saved to `expenses.json` in the project directory. Each entry has the following structure:

```json
{
  "id": "7c8667fa-41a5-4010-b693-382aa30f7980",
  "amount": 12.50,
  "category": "food",
  "description": "Lunch at cafe",
  "date": "2026-04-02 10:30:00"
}
```

## Testing

Run the test suite with pytest:

```bash
pytest test_expense_tracker.py -v
```

The suite covers all core classes: `Expense`, `InputValidator`, `JsonFileStorage`, `ExpenseTracker`, and `TableFormatter`.

## Project Structure

```
expense-tracker/
  expense_tracker.py       # All application code (models, storage, UI)
  test_expense_tracker.py  # Test suite (pytest)
  expenses.json            # Data file (created on first use)
```

## API Reference

### `Expense`

Dataclass representing a single expense entry.

- `Expense.create_new(amount, category, description)` — create a new expense with auto-generated ID and timestamp
- `to_dict()` — convert to dictionary for JSON serialisation
- `Expense.from_dict(data)` — create an expense from a dictionary

### `ExpenseTracker`

Main class managing expenses and operations.

**Constructor:**
- `ExpenseTracker(storage: DataStorage)` — initialise with a storage backend

**Methods:**

#### `add_expense(amount, category, description)`

Add a new expense and persist it to disk.

**Parameters:**
- `amount` (float): The expense amount (must be positive)
- `category` (str): Spending category (e.g. "food", "transport")
- `description` (str): Brief description of the expense

**Returns:**
- `Expense | None`: The created `Expense` if successful, `None` otherwise

#### `get_all_expenses()`

Retrieve all recorded expenses.

**Returns:**
- `list[Expense]`: Copy of all expense records

#### `calculate_total_spending()`

Calculate the sum of all expense amounts.

**Returns:**
- `float`: Total spending

#### `get_spending_by_category()`

Group and sum expenses by category.

**Returns:**
- `dict[str, float]`: Mapping of category name to total amount

#### `filter_by_category(category)`

Get expenses filtered by category (case-insensitive).

**Parameters:**
- `category` (str): The category to filter by

**Returns:**
- `list[Expense]`: Expenses matching the category

#### `get_available_categories()`

Get a sorted list of all unique categories.

**Returns:**
- `list[str]`: Unique category names

### `InputValidator`

Static validation methods for user input.

- `validate_amount(amount)` — returns `True` if amount is positive
- `validate_text_field(text)` — returns `True` if non-empty and at most 100 characters
- `validate_choice(choice, min_val, max_val)` — returns `True` if choice is within range

### `TableFormatter`

Static methods for formatting expense data in tables.

- `print_expenses_table(expenses)` — display all expenses in a formatted table
- `print_category_breakdown(category_totals)` — display spending by category with percentages
- `print_category_expenses(expenses, category)` — display expenses for a single category

### `DataStorage` (ABC)

Abstract base class for storage backends. Implement `save_expenses` and `load_expenses` to create a custom backend.

### `JsonFileStorage`

Default storage backend using a local JSON file.

- `JsonFileStorage(file_path="expenses.json")` — initialise with optional custom file path
- Implements `DataStorage` ABC — can be swapped for custom storage backends

### `ExpenseTrackerUI`

Interactive command-line interface.

- `ExpenseTrackerUI(tracker)` — initialise with an `ExpenseTracker` instance
- `run()` — start the interactive menu loop
