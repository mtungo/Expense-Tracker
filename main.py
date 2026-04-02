from expense import (
    add_expense,
    get_all_expenses,
    get_total_spending,
    get_spending_by_category,
)


def display_menu():
    print("\n=== Expense Tracker ===")
    print("1. Add expense")
    print("2. View all expenses")
    print("3. View total spending")
    print("4. View spending by category")
    print("5. Exit")
    return input("\nChoose an option (1-5): ").strip()


def handle_add():
    try:
        amount = float(input("Amount: "))
    except ValueError:
        print("Invalid amount.")
        return
    category = input("Category (e.g. food, transport, bills): ").strip()
    description = input("Description: ").strip()
    if not category or not description:
        print("Category and description cannot be empty.")
        return
    expense = add_expense(amount, category, description)
    print(f"Added: ${expense['amount']:.2f} - {expense['category']} - {expense['description']}")


def handle_view_all():
    expenses = get_all_expenses()
    if not expenses:
        print("No expenses recorded.")
        return
    print(f"\n{'ID':<5}{'Date':<22}{'Category':<15}{'Amount':<12}{'Description'}")
    print("-" * 70)
    for e in expenses:
        print(f"{e['id']:<5}{e['date']:<22}{e['category']:<15}${e['amount']:<11.2f}{e['description']}")


def handle_total():
    total = get_total_spending()
    print(f"\nTotal spending: ${total:.2f}")


def handle_by_category():
    totals = get_spending_by_category()
    if not totals:
        print("No expenses recorded.")
        return
    print(f"\n{'Category':<20}{'Total'}")
    print("-" * 35)
    for category, total in sorted(totals.items()):
        print(f"{category:<20}${total:.2f}")


def main():
    handlers = {
        "1": handle_add,
        "2": handle_view_all,
        "3": handle_total,
        "4": handle_by_category,
    }
    while True:
        choice = display_menu()
        if choice == "5":
            print("Goodbye!")
            break
        handler = handlers.get(choice)
        if handler:
            handler()
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
