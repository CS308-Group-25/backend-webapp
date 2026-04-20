from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from modules.orders.model import Order
from modules.orders.service import OrderService


def _make_service(order_repo=None, cart_repo=None, product_repo=None):
    return OrderService(
        order_repo=order_repo or MagicMock(),
        cart_repo=cart_repo or MagicMock(),
        product_repo=product_repo or MagicMock(),
    )


def test_get_order_by_id_wrong_user_raises_403():
    """T-047b: A customer accessing another customer's order receives 403."""
    order_repo = MagicMock()
    order = MagicMock(spec=Order)
    order.user_id = 1
    order_repo.get_by_order_id.return_value = order

    service = _make_service(order_repo=order_repo)

    with pytest.raises(HTTPException) as exc_info:
        service.get_order_by_id(order_id=42, user_id=2)

    assert exc_info.value.status_code == 403
    order_repo.get_by_order_id.assert_called_once_with(42)


def test_update_status_valid_transition():
    # Arrange
    order_repo = MagicMock()
    order = MagicMock(spec=Order)
    order.status = "confirmed"
    order_repo.get_by_order_id.return_value = order
    
    updated_order = MagicMock(spec=Order)
    updated_order.status = "processing"
    # To mock _build_order_response behavior, we need some attributes
    updated_order.id = 1
    updated_order.total = 100.0
    updated_order.invoice = None
    updated_order.delivery_address = "Address"
    from datetime import datetime, timezone
    updated_order.created_at = datetime.now(timezone.utc)
    updated_order.items = []

    
    order_repo.update_order_status.return_value = updated_order
    
    service = _make_service(order_repo=order_repo)
    
    # Act
    result = service.update_order_status(order_id=1, new_status="processing")
    
    # Assert
    assert result.status == "processing"
    order_repo.update_order_status.assert_called_once_with(1, "processing")


def test_update_status_invalid_transition_raises_400():
    # Arrange
    order_repo = MagicMock()
    order = MagicMock(spec=Order)
    order.status = "delivered"
    order_repo.get_by_order_id.return_value = order
    
    service = _make_service(order_repo=order_repo)
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        service.update_order_status(order_id=1, new_status="processing")
    
    assert exc_info.value.status_code == 400
    assert "Invalid status transition" in exc_info.value.detail
    order_repo.update_order_status.assert_not_called()


def test_update_status_order_not_found_raises_404():
    # Arrange
    order_repo = MagicMock()
    order_repo.get_by_order_id.return_value = None
    
    service = _make_service(order_repo=order_repo)
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        service.update_order_status(order_id=999, new_status="processing")
    
    assert exc_info.value.status_code == 404
    order_repo.update_order_status.assert_not_called()


def test_update_status_same_status_no_update_called():
    """T-212: Updating to the same status should not call the repository update."""
    # Arrange
    order_repo = MagicMock()
    order = MagicMock(spec=Order)
    order.id = 1
    order.status = "processing"
    order.total = 100.0
    order.invoice = None
    order.delivery_address = "Address"
    from datetime import datetime, timezone
    order.created_at = datetime.now(timezone.utc)
    order.items = []
    
    order_repo.get_by_order_id.return_value = order
    
    service = _make_service(order_repo=order_repo)
    
    # Act
    result = service.update_order_status(order_id=1, new_status="processing")
    
    # Assert
    assert result.status == "processing"
    # Ensure update_order_status was NEVER called because status didn't change
    order_repo.update_order_status.assert_not_called()

