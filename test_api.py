"""Tests for the Expense Tracker REST API."""

import os
import sys
import json
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from api.main import app
from api.dependencies import get_tracker
from expense_tracker import ExpenseTracker, JsonFileStorage


@pytest.fixture
def temp_storage(tmp_path):
    """Create a temporary storage for testing."""
    file_path = str(tmp_path / "test_expenses.json")
    return JsonFileStorage(file_path)


@pytest.fixture
def tracker(temp_storage):
    """Create a fresh tracker for each test."""
    return ExpenseTracker(temp_storage)


@pytest.fixture
def client(tracker):
    """Create a test client with isolated tracker."""
    app.dependency_overrides[get_tracker] = lambda: tracker
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_expenses(tracker):
    """Add sample expenses to the tracker."""
    tracker.add_expense(12.50, "food", "Lunch at cafe")
    tracker.add_expense(35.00, "transport", "Taxi ride")
    tracker.add_expense(8.75, "food", "Coffee and snack")
    tracker.add_expense(50.00, "entertainment", "Concert tickets")
    return tracker


# === Root Endpoint ===

class TestRootEndpoint:
    def test_root_returns_api_info(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Expense Tracker API"
        assert "endpoints" in data


# === GET /api/v1/expenses ===

class TestListExpenses:
    def test_empty_list(self, client):
        response = client.get("/api/v1/expenses")
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["meta"]["total"] == 0

    def test_list_all_expenses(self, client, sample_expenses):
        response = client.get("/api/v1/expenses")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["total"] == 4
        assert len(data["data"]) == 4

    def test_pagination(self, client, sample_expenses):
        response = client.get("/api/v1/expenses?page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["meta"]["total"] == 4
        assert data["meta"]["page"] == 1
        assert data["meta"]["page_size"] == 2
        assert data["meta"]["total_pages"] == 2
        assert data["links"]["next"] is not None
        assert data["links"]["prev"] is None

    def test_pagination_page_2(self, client, sample_expenses):
        response = client.get("/api/v1/expenses?page=2&page_size=2")
        data = response.json()
        assert len(data["data"]) == 2
        assert data["links"]["prev"] is not None

    def test_filter_by_category(self, client, sample_expenses):
        response = client.get("/api/v1/expenses?category=food")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["total"] == 2
        for expense in data["data"]:
            assert expense["category"].lower() == "food"

    def test_sort_by_amount_asc(self, client, sample_expenses):
        response = client.get("/api/v1/expenses?sort=amount&order=asc")
        data = response.json()
        amounts = [e["amount"] for e in data["data"]]
        assert amounts == sorted(amounts)

    def test_sort_by_amount_desc(self, client, sample_expenses):
        response = client.get("/api/v1/expenses?sort=amount&order=desc")
        data = response.json()
        amounts = [e["amount"] for e in data["data"]]
        assert amounts == sorted(amounts, reverse=True)


# === POST /api/v1/expenses ===

class TestCreateExpense:
    def test_create_expense(self, client):
        response = client.post("/api/v1/expenses", json={
            "amount": 25.00,
            "category": "food",
            "description": "Dinner"
        })
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["amount"] == 25.00
        assert data["category"] == "food"
        assert data["description"] == "Dinner"
        assert "id" in data
        assert "date" in data

    def test_create_expense_invalid_amount(self, client):
        response = client.post("/api/v1/expenses", json={
            "amount": -5.00,
            "category": "food",
            "description": "Bad"
        })
        assert response.status_code == 422

    def test_create_expense_missing_field(self, client):
        response = client.post("/api/v1/expenses", json={
            "amount": 10.00,
            "category": "food"
        })
        assert response.status_code == 422

    def test_create_expense_empty_category(self, client):
        response = client.post("/api/v1/expenses", json={
            "amount": 10.00,
            "category": "",
            "description": "Test"
        })
        assert response.status_code == 422


# === GET /api/v1/expenses/{id} ===

class TestGetExpense:
    def test_get_existing_expense(self, client):
        create_resp = client.post("/api/v1/expenses", json={
            "amount": 15.00,
            "category": "food",
            "description": "Snack"
        })
        expense_id = create_resp.json()["data"]["id"]

        response = client.get(f"/api/v1/expenses/{expense_id}")
        assert response.status_code == 200
        assert response.json()["data"]["id"] == expense_id

    def test_get_nonexistent_expense(self, client):
        response = client.get("/api/v1/expenses/nonexistent-id")
        assert response.status_code == 404


# === PATCH /api/v1/expenses/{id} ===

class TestUpdateExpense:
    def test_update_amount(self, client):
        create_resp = client.post("/api/v1/expenses", json={
            "amount": 10.00,
            "category": "food",
            "description": "Original"
        })
        expense_id = create_resp.json()["data"]["id"]

        response = client.patch(f"/api/v1/expenses/{expense_id}", json={
            "amount": 20.00
        })
        assert response.status_code == 200
        assert response.json()["data"]["amount"] == 20.00
        assert response.json()["data"]["description"] == "Original"

    def test_update_category(self, client):
        create_resp = client.post("/api/v1/expenses", json={
            "amount": 10.00,
            "category": "food",
            "description": "Test"
        })
        expense_id = create_resp.json()["data"]["id"]

        response = client.patch(f"/api/v1/expenses/{expense_id}", json={
            "category": "transport"
        })
        assert response.status_code == 200
        assert response.json()["data"]["category"] == "transport"

    def test_update_nonexistent(self, client):
        response = client.patch("/api/v1/expenses/nonexistent", json={
            "amount": 5.00
        })
        assert response.status_code == 404

    def test_update_invalid_amount(self, client):
        create_resp = client.post("/api/v1/expenses", json={
            "amount": 10.00,
            "category": "food",
            "description": "Test"
        })
        expense_id = create_resp.json()["data"]["id"]

        response = client.patch(f"/api/v1/expenses/{expense_id}", json={
            "amount": -5.00
        })
        assert response.status_code == 422


# === DELETE /api/v1/expenses/{id} ===

class TestDeleteExpense:
    def test_delete_expense(self, client):
        create_resp = client.post("/api/v1/expenses", json={
            "amount": 10.00,
            "category": "food",
            "description": "To delete"
        })
        expense_id = create_resp.json()["data"]["id"]

        response = client.delete(f"/api/v1/expenses/{expense_id}")
        assert response.status_code == 204

        # Verify it's gone
        get_resp = client.get(f"/api/v1/expenses/{expense_id}")
        assert get_resp.status_code == 404

    def test_delete_nonexistent(self, client):
        response = client.delete("/api/v1/expenses/nonexistent")
        assert response.status_code == 404


# === GET /api/v1/categories ===

class TestCategories:
    def test_empty_categories(self, client):
        response = client.get("/api/v1/categories")
        assert response.status_code == 200
        assert response.json()["data"] == []

    def test_categories_with_data(self, client, sample_expenses):
        response = client.get("/api/v1/categories")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 3
        categories = [c["category"] for c in data]
        assert "food" in categories
        assert "transport" in categories
        assert "entertainment" in categories

    def test_category_percentages_sum_to_100(self, client, sample_expenses):
        response = client.get("/api/v1/categories")
        data = response.json()["data"]
        total_pct = sum(c["percentage"] for c in data)
        assert abs(total_pct - 100.0) < 0.5  # Allow rounding tolerance


# === GET /api/v1/summary ===

class TestSummary:
    def test_empty_summary(self, client):
        response = client.get("/api/v1/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["total_spending"] == 0
        assert data["total_expenses"] == 0
        assert data["categories_count"] == 0

    def test_summary_with_data(self, client, sample_expenses):
        response = client.get("/api/v1/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["total_spending"] == 106.25
        assert data["total_expenses"] == 4
        assert data["categories_count"] == 3
        assert len(data["by_category"]) == 3
