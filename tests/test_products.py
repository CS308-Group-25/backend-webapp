from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from core.dependencies import get_current_user
from main import app
from modules.auth.model import User


# Mock user for testing
@pytest.fixture
def mock_product_manager():
    return User(
        id=1,
        name="Product Manager",
        email="pm@example.com",
        role="product_manager"
    )


@pytest.fixture
def mock_customer():
    return User(
        id=2,
        name="Customer",
        email="customer@example.com",
        role="customer"
    )


def test_create_product_success(client: TestClient, mock_product_manager):
    # Override dependency to return mock product manager
    app.dependency_overrides[get_current_user] = lambda: mock_product_manager
    
    product_data = {
        "name": "Whey Protein",
        "model": "Gold Standard",
        "serial_no": "WHEY-123",
        "description": "High quality whey protein",
        "stock": 100,
        "warranty": "2 years",
        "distributor": "Optimum Nutrition",
        "brand": "ON",
        "flavor": "Chocolate",
        "form": "Powder",
        "serving_size": "30g",
        "goal_tags": "muscle-gain,recovery",
        "category_id": 1
    }
    
    # Mock DB session in router might be tricky. Let's just test if the endpoint
    # is called and returns 201, assuming the implementation works (or we can
    # mock the DB session too).
    
    # For now, let's see if we can just run it. We might need a database
    # for a real test, but since this is a unit test, we should mock the
    # DB session.
    
    from datetime import datetime, timezone

    from core.database import get_db
    mock_db = MagicMock()
    
    # Simulate DB setting id and created_at
    def mock_add(obj):
        obj.id = 1
        obj.created_at = datetime.now(timezone.utc)
        return obj

    mock_db.add.side_effect = mock_add
    app.dependency_overrides[get_db] = lambda: mock_db
    
    response = client.post("/api/v1/admin/products/", json=product_data)
    
    assert response.status_code == 201
    assert response.json()["name"] == "Whey Protein"
    assert response.json()["id"] == 1
    assert "created_at" in response.json()
    
    # Clean up overrides
    app.dependency_overrides.clear()


def test_create_product_forbidden_for_customer(client: TestClient, mock_customer):
    app.dependency_overrides[get_current_user] = lambda: mock_customer
    
    product_data = {
        "name": "Illegal Product",
        "stock": 1
    }
    
    response = client.post("/api/v1/admin/products/", json=product_data)
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Only product managers can perform this action"
    
    app.dependency_overrides.clear()
