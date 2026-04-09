from unittest.mock import MagicMock

import pytest

from modules.products.model import Product
from modules.products.schema import ProductCreate
from modules.products.service import ProductService


@pytest.fixture
def mock_db():
    return MagicMock()

def test_service_create_product():
    mock_repo = MagicMock()
    service = ProductService(mock_repo)
    
    product_in = ProductCreate(
        name="Whey Protein",
        model="Gold Standard",
        serial_no="WHEY-123",
        description="High quality whey protein",
        stock=100,
        warranty="2 years",
        distributor="Optimum Nutrition",
        brand="ON",
        flavor="Chocolate",
        form="Powder",
        serving_size="30g",
        goal_tags="muscle-gain,recovery",
        category_id=1
    )
    
    # Setup mock return value
    expected_product = Product(id=1, **product_in.model_dump())
    mock_repo.create_product.return_value = expected_product
    
    result = service.create_product(product_in)
    
    assert result.id == 1
    assert result.name == "Whey Protein"
    mock_repo.create_product.assert_called_once_with(product_in.model_dump())

def test_list_returns_all_products():
    mock_repo = MagicMock()
    service = ProductService(mock_repo)

    expected = [Product(id=1, name="Whey"), Product(id=2, name="Creatine")]
    mock_repo.get_all.return_value = expected

    result = service.list_products()

    assert result == expected
    assert len(result) == 2
    mock_repo.get_all.assert_called_once()

def test_get_by_id_returns_correct_product():
    mock_repo = MagicMock()
    service = ProductService(mock_repo)

    expected = Product(id=5, name="BCAA")
    mock_repo.get_by_id.return_value = expected

    result = service.get_product(5)

    assert result.id == 5
    assert result.name == "BCAA"
    mock_repo.get_by_id.assert_called_once_with(5)