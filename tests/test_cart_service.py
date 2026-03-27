from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from modules.cart.model import Cart, CartItem
from modules.cart.service import CartService
from modules.products.model import Product


def test_add_item_success():
    # Arrange
    mock_cart_repo = MagicMock()
    mock_product_repo = MagicMock()

    # Mock product with enough stock
    mock_product = MagicMock(spec=Product)
    mock_product.id = 100
    mock_product.stock = 5
    mock_product_repo.get_by_id.return_value = mock_product

    # Mock cart retrieval
    mock_cart = MagicMock(spec=Cart)
    mock_cart.id = 50
    mock_cart_repo.get.return_value = mock_cart

    # Mock add_item response
    mock_cart_item = MagicMock(spec=CartItem)
    mock_cart_item.id = 200
    mock_cart_item.cart_id = 50
    mock_cart_item.product_id = 100
    mock_cart_item.quantity = 2
    mock_cart_repo.add_item.return_value = mock_cart_item

    service = CartService(repo=mock_cart_repo, product_repo=mock_product_repo)

    # Act
    result = service.add_item(user_id=1, product_id=100, quantity=2)

    # Assert
    assert result.product_id == 100
    assert result.quantity == 2
    mock_product_repo.get_by_id.assert_called_once_with(100)
    mock_cart_repo.get.assert_called_once_with(1)
    mock_cart_repo.add_item.assert_called_once_with(50, 100, 2)


def test_add_item_out_of_stock_raises_400():
    # Arrange
    mock_cart_repo = MagicMock()
    mock_product_repo = MagicMock()

    # Product exists but stock is only 1
    mock_product = MagicMock(spec=Product)
    mock_product.id = 100
    mock_product.stock = 1
    mock_product_repo.get_by_id.return_value = mock_product

    service = CartService(repo=mock_cart_repo, product_repo=mock_product_repo)

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        service.add_item(user_id=1, product_id=100, quantity=2)

    # Assert 400 Out of stock
    assert exc.value.status_code == 400
    assert exc.value.detail == "Not enough stock"

    # Ensure add_item was never called in the repo!
    mock_cart_repo.add_item.assert_not_called()


def test_remove_item_success():
    # Arrange
    mock_cart_repo = MagicMock()
    mock_product_repo = MagicMock()

    # Setup the repo to return True for successful deletion
    mock_cart_repo.remove_item.return_value = True

    service = CartService(repo=mock_cart_repo, product_repo=mock_product_repo)

    # Act
    result = service.remove_item(cart_item_id=200)

    # Assert
    assert result is True
    mock_cart_repo.remove_item.assert_called_once_with(200)
