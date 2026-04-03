"""Summary endpoints."""

from fastapi import APIRouter, Depends

from api.schemas import SummaryResponse, CategoryTotal
from api.dependencies import get_tracker
from expense_tracker import ExpenseTracker

router = APIRouter(prefix="/summary", tags=["Summary"])


@router.get("", response_model=SummaryResponse)
def get_summary(
    tracker: ExpenseTracker = Depends(get_tracker),
):
    """Get overall spending summary with category breakdown."""
    expenses = tracker.get_all_expenses()
    category_totals = tracker.get_spending_by_category()
    total_spending = tracker.calculate_total_spending()
    categories = tracker.get_available_categories()

    by_category = []
    for category, amount in sorted(category_totals.items()):
        percentage = (amount / total_spending * 100) if total_spending > 0 else 0
        by_category.append(CategoryTotal(
            category=category,
            total=round(amount, 2),
            percentage=round(percentage, 1),
        ))

    return SummaryResponse(
        total_spending=round(total_spending, 2),
        total_expenses=len(expenses),
        categories_count=len(categories),
        by_category=by_category,
    )
