from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from modules.orders.model import Order
from modules.orders.service import OrderService


def _make_service(order_repo=None):
    return OrderService(
        order_repo=order_repo or MagicMock(),
        cart_repo=MagicMock(),
        product_repo=MagicMock(),
        invoice_service=MagicMock(),
    )


def test_cancel_order_success_when_pending():
    """T-203: Cancelling a pending order succeeds and updates status to cancelled."""
    order_repo = MagicMock()

    order = MagicMock(spec=Order)
    order.id = 1
    order.user_id = 42
    order.status = "pending"

    cancelled_order = MagicMock(spec=Order)
    cancelled_order.id = 1
    cancelled_order.status = "cancelled"
    cancelled_order.total = 100.0
    cancelled_order.invoice = None
    cancelled_order.delivery_address = "123 Test St"
    cancelled_order.created_at = datetime.now(timezone.utc)
    cancelled_order.items = []

    order_repo.get_by_order_id.return_value = order
    order_repo.update_order_status.return_value = cancelled_order

    service = _make_service(order_repo=order_repo)

    result = service.cancel_order(order_id=1, user_id=42)

    assert result.status == "cancelled"
    order_repo.update_order_status.assert_called_once_with(1, "cancelled")


def test_cancel_order_returns_400_when_processing():
    """T-203: Cancelling a processing order raises 400 and never touches the repo."""
    order_repo = MagicMock()

    order = MagicMock(spec=Order)
    order.id = 1
    order.user_id = 42
    order.status = "processing"

    order_repo.get_by_order_id.return_value = order

    service = _make_service(order_repo=order_repo)

    with pytest.raises(HTTPException) as exc_info:
        service.cancel_order(order_id=1, user_id=42)

    assert exc_info.value.status_code == 400
    order_repo.update_order_status.assert_not_called()
