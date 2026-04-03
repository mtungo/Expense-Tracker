"""Pydantic schemas for request/response validation."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ExpenseCreate(BaseModel):
    """Schema for creating a new expense."""
    amount: float = Field(..., gt=0, description="Expense amount (must be positive)")
    category: str = Field(..., min_length=1, max_length=100, description="Expense category")
    description: str = Field(..., min_length=1, max_length=100, description="Expense description")


class ExpenseUpdate(BaseModel):
    """Schema for partially updating an expense."""
    amount: Optional[float] = Field(None, gt=0, description="New expense amount")
    category: Optional[str] = Field(None, min_length=1, max_length=100, description="New category")
    description: Optional[str] = Field(None, min_length=1, max_length=100, description="New description")


class ExpenseResponse(BaseModel):
    """Schema for a single expense in responses."""
    id: str
    amount: float
    category: str
    description: str
    date: str


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginationLinks(BaseModel):
    """Pagination links."""
    self_link: str = Field(..., alias="self")
    next: Optional[str] = None
    prev: Optional[str] = None

    model_config = {"populate_by_name": True}


class ExpenseListResponse(BaseModel):
    """Paginated list of expenses."""
    data: List[ExpenseResponse]
    meta: PaginationMeta
    links: PaginationLinks


class SingleExpenseResponse(BaseModel):
    """Single expense wrapper."""
    data: ExpenseResponse


class CategoryTotal(BaseModel):
    """Category with total spending."""
    category: str
    total: float
    percentage: float


class CategoryListResponse(BaseModel):
    """List of categories with totals."""
    data: List[CategoryTotal]


class SummaryResponse(BaseModel):
    """Overall spending summary."""
    total_spending: float
    total_expenses: int
    categories_count: int
    by_category: List[CategoryTotal]


class ErrorDetail(BaseModel):
    """Individual error detail."""
    field: Optional[str] = None
    issue: str


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: dict
