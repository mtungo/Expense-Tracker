"""Expense CRUD endpoints."""

import math
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from api.schemas import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse,
    ExpenseListResponse,
    SingleExpenseResponse,
    PaginationMeta,
    PaginationLinks,
)
from api.dependencies import get_tracker
from expense_tracker import ExpenseTracker

router = APIRouter(prefix="/expenses", tags=["Expenses"])


def _expense_to_response(expense) -> ExpenseResponse:
    """Convert an Expense dataclass to a response schema."""
    return ExpenseResponse(
        id=expense.expense_id,
        amount=expense.amount,
        category=expense.category,
        description=expense.description,
        date=expense.date,
    )


@router.get("", response_model=ExpenseListResponse)
def list_expenses(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    sort: str = Query("date", description="Sort field (date, amount, category)"),
    order: str = Query("desc", description="Sort order (asc, desc)"),
    tracker: ExpenseTracker = Depends(get_tracker),
):
    """List all expenses with pagination and optional filtering."""
    if category:
        expenses = tracker.filter_by_category(category)
    else:
        expenses = tracker.get_all_expenses()

    # Sort
    sort_key_map = {
        "date": lambda e: e.date,
        "amount": lambda e: e.amount,
        "category": lambda e: e.category.lower(),
    }
    sort_fn = sort_key_map.get(sort, sort_key_map["date"])
    reverse = order.lower() == "desc"
    expenses.sort(key=sort_fn, reverse=reverse)

    # Paginate
    total = len(expenses)
    total_pages = max(1, math.ceil(total / page_size))
    start = (page - 1) * page_size
    end = start + page_size
    page_expenses = expenses[start:end]

    base_url = "/api/v1/expenses"
    params = f"page_size={page_size}"
    if category:
        params += f"&category={category}"
    params += f"&sort={sort}&order={order}"

    return ExpenseListResponse(
        data=[_expense_to_response(e) for e in page_expenses],
        meta=PaginationMeta(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        ),
        links=PaginationLinks(
            **{
                "self": f"{base_url}?page={page}&{params}",
                "next": f"{base_url}?page={page + 1}&{params}" if page < total_pages else None,
                "prev": f"{base_url}?page={page - 1}&{params}" if page > 1 else None,
            }
        ),
    )


@router.post("", response_model=SingleExpenseResponse, status_code=201)
def create_expense(
    body: ExpenseCreate,
    tracker: ExpenseTracker = Depends(get_tracker),
):
    """Create a new expense."""
    expense = tracker.add_expense(body.amount, body.category, body.description)
    if expense is None:
        raise HTTPException(
            status_code=422,
            detail={"error": {"code": "VALIDATION_ERROR", "message": "Invalid expense data"}},
        )
    return SingleExpenseResponse(data=_expense_to_response(expense))


@router.get("/{expense_id}", response_model=SingleExpenseResponse)
def get_expense(
    expense_id: str,
    tracker: ExpenseTracker = Depends(get_tracker),
):
    """Get a single expense by ID."""
    expense = tracker.get_expense_by_id(expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return SingleExpenseResponse(data=_expense_to_response(expense))


@router.patch("/{expense_id}", response_model=SingleExpenseResponse)
def update_expense(
    expense_id: str,
    body: ExpenseUpdate,
    tracker: ExpenseTracker = Depends(get_tracker),
):
    """Partially update an expense."""
    existing = tracker.get_expense_by_id(expense_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Expense not found")

    updated = tracker.update_expense(
        expense_id,
        amount=body.amount,
        category=body.category,
        description=body.description,
    )
    if updated is None:
        raise HTTPException(
            status_code=422,
            detail={"error": {"code": "VALIDATION_ERROR", "message": "Invalid update data"}},
        )
    return SingleExpenseResponse(data=_expense_to_response(updated))


@router.delete("/{expense_id}", status_code=204)
def delete_expense(
    expense_id: str,
    tracker: ExpenseTracker = Depends(get_tracker),
):
    """Delete an expense."""
    deleted = tracker.delete_expense(expense_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")
