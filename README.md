# Expense Tracker

A command-line expense tracker that lets you record, view, and analyze personal spending. Data is stored locally in a JSON file.

## Requirements

- Python 3.7+

No external dependencies required — uses only the Python standard library.

## Usage

```bash
python main.py
```

This launches an interactive menu:

```
=== Expense Tracker ===
1. Add expense
2. View all expenses
3. View total spending
4. View spending by category
5. Exit
```

### Adding an Expense

Select option `1` and enter the amount, category, and description when prompted:

```
Amount: 12.50
Category (e.g. food, transport, bills): food
Description: Lunch at cafe
Added: $12.50 - food - Lunch at cafe
```

### Viewing Expenses

Select option `2` to see all recorded expenses in a table:

```
ID   Date                  Category       Amount      Description
----------------------------------------------------------------------
1    2026-04-02 10:30:00   food           $12.50      Lunch at cafe
2    2026-04-02 14:00:00   transport      $3.25       Bus fare
```

### Spending Summary

- Option `3` — view total spending across all categories
- Option `4` — view spending broken down by category

## Data Storage

Expenses are saved to `expenses.json` in the project directory. Each entry has the following structure:

```json
{
  "id": 1,
  "amount": 12.50,
  "category": "food",
  "description": "Lunch at cafe",
  "date": "2026-04-02 10:30:00"
}
```

## Project Structure

```
expense-tracker/
  main.py         # CLI interface and menu handlers
  expense.py      # Data layer: load, save, query expenses
  expenses.json   # Data file (created on first use)
```

## API Reference

The `expense` module exposes four public functions for programmatic use:

### `add_expense(amount, category, description)`

Add a new expense and persist it to disk.

**Parameters:**
- `amount` (float): The expense amount
- `category` (str): Spending category (e.g. "food", "transport")
- `description` (str): Brief description of the expense

**Returns:**
- `dict`: The created expense record with `id`, `amount`, `category`, `description`, and `date`

### `get_all_expenses()`

Retrieve all recorded expenses.

**Returns:**
- `list[dict]`: All expense records

### `get_total_spending()`

Calculate the sum of all expense amounts.

**Returns:**
- `float`: Total spending, rounded to 2 decimal places

### `get_spending_by_category()`

Group and sum expenses by category.

**Returns:**
- `dict[str, float]`: Mapping of category name to total amount
