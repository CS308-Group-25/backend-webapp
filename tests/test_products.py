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
    
    # Mock ProductService.create_product
    from datetime import datetime, timezone
    from modules.products.service import ProductService
    from modules.products.model import Product
    
    mock_product = Product(
        id=1, 
        created_at=datetime.now(timezone.utc),
        **product_data
    )
    
    mock_service = MagicMock(spec=ProductService)
    mock_service.create_product.return_value = mock_product
    
    # We need to mock the service instantiation in the router
    # Since the router does: service = ProductService(db)
    with MagicMock() as mock_db:
        # Instead of mocking the DB, we can mock the ProductService class in the router module
        import modules.products.router
        with MagicMock() as mock_service_class:
            mock_service_class.return_value = mock_service
            
            # Save original
            original_service_class = modules.products.router.ProductService
            modules.products.router.ProductService = mock_service_class
            
            try:
                response = client.post("/api/v1/admin/products/", json=product_data)
                
                assert response.status_code == 201
                assert response.json()["name"] == "Whey Protein"
                assert response.json()["id"] == 1
                assert "created_at" in response.json()
                
                mock_service.create_product.assert_called_once()
            finally:
                # Restore original
                modules.products.router.ProductService = original_service_class

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
