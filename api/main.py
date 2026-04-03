"""FastAPI application entry point for the Expense Tracker REST API."""

import os
import sys

# Ensure the project root is on the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from api.routes import expenses, categories, summary

app = FastAPI(
    title="Expense Tracker API",
    description="RESTful API for managing personal expenses",
    version="1.0.0",
)

# Mount all routes under /api/v1
app.include_router(expenses.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(summary.router, prefix="/api/v1")


@app.get("/", tags=["Root"])
def root():
    """API root - health check and version info."""
    return {
        "name": "Expense Tracker API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "expenses": "/api/v1/expenses",
            "categories": "/api/v1/categories",
            "summary": "/api/v1/summary",
        },
    }
