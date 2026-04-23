from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from core.dependencies import get_current_user
from main import app
from modules.auth.model import User
from modules.cart.router import get_cart_service


@pytest.fixture
def mock_user():
    return User(id=1, email="test@example.com", name="Test User", role="customer")


def test_update_cart_item_not_found_returns_404(mock_user):
    # 1. Setup mocks
    mock_service = MagicMock()
    # Simulate item not found by returning None
    mock_service.update_item.return_value = None
    # Simulate verify passing (or failing, either way update_item check is the goal)
    mock_service.verify_item_ownership.return_value = None

    # 2. Override dependencies
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_cart_service] = lambda: mock_service

    with TestClient(app) as client:
        response = client.patch("/api/v1/cart/items/999", json={"quantity": 5})

        assert response.status_code == 404
        assert response.json()["detail"] == "Cart item not found"

    # 3. Clean up
    app.dependency_overrides.clear()
