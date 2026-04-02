from unittest.mock import MagicMock, patch

import pytest

from modules.products.model import Product
from modules.products.schema import ProductCreate
from modules.products.service import ProductService


@pytest.fixture
def mock_db():
    return MagicMock()

def test_service_create_product(mock_db):
    with patch("modules.products.service.ProductRepository") as MockRepository:
        service = ProductService(mock_db)
        
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
        MockRepository.return_value.create_product.return_value = expected_product
        
        result = service.create_product(product_in)
        
        assert result.id == 1
        assert result.name == "Whey Protein"
        MockRepository.return_value.create_product.assert_called_once_with(product_in.model_dump())

def test_service_get_product(mock_db):
    with patch("modules.products.service.ProductRepository") as MockRepository:
        service = ProductService(mock_db)
        
        expected_product = Product(id=1, name="Whey Protein")
        MockRepository.return_value.get_by_id.return_value = expected_product
        
        result = service.get_product(1)
        
        assert result.id == 1
        assert result.name == "Whey Protein"
        MockRepository.return_value.get_by_id.assert_called_once_with(1)
