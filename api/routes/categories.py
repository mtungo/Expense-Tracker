"""Category endpoints."""

from fastapi import APIRouter, Depends

from api.schemas import CategoryListResponse, CategoryTotal
from api.dependencies import get_tracker
from expense_tracker import ExpenseTracker

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=CategoryListResponse)
def list_categories(
    tracker: ExpenseTracker = Depends(get_tracker),
):
    """List all categories with their spending totals and percentages."""
    category_totals = tracker.get_spending_by_category()
    total_spending = sum(category_totals.values())

    data = []
    for category, amount in sorted(category_totals.items()):
        percentage = (amount / total_spending * 100) if total_spending > 0 else 0
        data.append(CategoryTotal(
            category=category,
            total=round(amount, 2),
            percentage=round(percentage, 1),
        ))

    return CategoryListResponse(data=data)
