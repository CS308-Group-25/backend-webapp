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
