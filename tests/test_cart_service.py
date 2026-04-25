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


def test_verify_item_ownership_success():
    """Cart item belongs to the current user's cart — no exception raised."""
    mock_cart_repo = MagicMock()
    mock_product_repo = MagicMock()

    mock_cart_item = MagicMock(spec=CartItem)
    mock_cart_item.cart_id = 50
    mock_cart_repo.get_item_by_id.return_value = mock_cart_item

    mock_cart = MagicMock(spec=Cart)
    mock_cart.id = 50
    mock_cart_repo.get.return_value = mock_cart

    service = CartService(repo=mock_cart_repo, product_repo=mock_product_repo)

    # Should not raise
    service.verify_item_ownership(cart_item_id=200, user_id=1)

    mock_cart_repo.get_item_by_id.assert_called_once_with(200)
    mock_cart_repo.get.assert_called_once_with(1)


def test_verify_item_ownership_item_not_found():
    """Cart item does not exist — should raise 404."""
    mock_cart_repo = MagicMock()
    mock_product_repo = MagicMock()

    mock_cart_repo.get_item_by_id.return_value = None

    service = CartService(repo=mock_cart_repo, product_repo=mock_product_repo)

    with pytest.raises(HTTPException) as exc:
        service.verify_item_ownership(cart_item_id=999, user_id=1)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Cart item not found"


def test_verify_item_ownership_wrong_user():
    """Cart item belongs to a different user — should raise 403."""
    mock_cart_repo = MagicMock()
    mock_product_repo = MagicMock()

    # Cart item belongs to cart 50
    mock_cart_item = MagicMock(spec=CartItem)
    mock_cart_item.cart_id = 50
    mock_cart_repo.get_item_by_id.return_value = mock_cart_item

    # But user 2's cart has id 99
    mock_cart = MagicMock(spec=Cart)
    mock_cart.id = 99
    mock_cart_repo.get.return_value = mock_cart

    service = CartService(repo=mock_cart_repo, product_repo=mock_product_repo)

    with pytest.raises(HTTPException) as exc:
        service.verify_item_ownership(cart_item_id=200, user_id=2)

    assert exc.value.status_code == 403
    assert exc.value.detail == "This cart item does not belong to you"


def test_verify_item_ownership_no_cart_for_user():
    """User has no cart at all — should raise 403."""
    mock_cart_repo = MagicMock()
    mock_product_repo = MagicMock()

    mock_cart_item = MagicMock(spec=CartItem)
    mock_cart_item.cart_id = 50
    mock_cart_repo.get_item_by_id.return_value = mock_cart_item

    # User has no cart
    mock_cart_repo.get.return_value = None

    service = CartService(repo=mock_cart_repo, product_repo=mock_product_repo)

    with pytest.raises(HTTPException) as exc:
        service.verify_item_ownership(cart_item_id=200, user_id=3)

    assert exc.value.status_code == 403
    assert exc.value.detail == "This cart item does not belong to you"


def test_bulk_add_items_success():
    # Arrange
    mock_cart_repo = MagicMock()
    mock_product_repo = MagicMock()

    mock_product = MagicMock(spec=Product)
    mock_product.id = 1
    mock_product.stock = 10
    mock_product_repo.get_by_id.return_value = mock_product

    mock_cart = MagicMock(spec=Cart)
    mock_cart.id = 50
    mock_cart_repo.get.return_value = mock_cart

    mock_cart_item = MagicMock(spec=CartItem)
    mock_cart_repo.bulk_add_items.return_value = [mock_cart_item]

    service = CartService(repo=mock_cart_repo, product_repo=mock_product_repo)

    # Act
    result = service.bulk_add_items(user_id=1, items=[{"product_id": 1, "quantity": 2}])

    # Assert
    assert len(result["added"]) == 1
    assert len(result["rejected"]) == 0
    mock_cart_repo.bulk_add_items.assert_called_once_with(
        50, [{"product_id": 1, "quantity": 2}])


def test_bulk_add_items_partial_out_of_stock_rejection():
    # Arrange
    mock_cart_repo = MagicMock()
    mock_product_repo = MagicMock()

    mock_cart = MagicMock(spec=Cart)
    mock_cart.id = 50
    mock_cart_repo.get.return_value = mock_cart

    # product 1 - enough stock
    mock_product_1 = MagicMock(spec=Product)
    mock_product_1.id = 1
    mock_product_1.stock = 10

    # product 2 — out of stock
    mock_product_2 = MagicMock(spec=Product)
    mock_product_2.id = 2
    mock_product_2.stock = 1

    mock_product_repo.get_by_id.side_effect = [mock_product_1, mock_product_2]

    mock_cart_item = MagicMock(spec=CartItem)
    mock_cart_repo.bulk_add_items.return_value = [mock_cart_item]

    service = CartService(repo=mock_cart_repo, product_repo=mock_product_repo)

    # Act
    result = service.bulk_add_items(
        user_id=1,
        items=[
            {"product_id": 1, "quantity": 2},
            {"product_id": 2, "quantity": 5},
        ],
    )

    # Assert
    assert len(result["added"]) == 1
    assert len(result["rejected"]) == 1
    assert result["rejected"][0]["product_id"] == 2
    assert result["rejected"][0]["reason"] == "Not enough stock"