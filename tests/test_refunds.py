from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from modules.refunds.service import RefundService


def _make_order_item(item_id=1, order_id=10, price=Decimal("100.00"), quantity=2):
    item = MagicMock()
    item.id = item_id
    item.order_id = order_id
    item.price = price
    item.quantity = quantity
    return item


def _make_order(order_id=10, user_id=1, status="delivered", days_ago=29):
    order = MagicMock()
    order.id = order_id
    order.user_id = user_id
    order.status = status
    order.created_at = datetime.now(timezone.utc) - timedelta(days=days_ago)
    order.items = [_make_order_item(item_id=1, order_id=order_id)]
    return order


def _make_service(order=None, active_request=None):
    refund_repo = MagicMock()
    refund_repo.get_active_request_for_item.return_value = active_request

    mock_refund = MagicMock()
    mock_refund.status = "requested"
    mock_refund.refund_amount = Decimal("200.00")
    refund_repo.create.return_value = mock_refund

    order_repo = MagicMock()
    order_repo.get_by_order_id.return_value = order

    service = RefundService(refund_repo=refund_repo, order_repo=order_repo)
    return service, refund_repo, order_repo


def test_request_refund_within_30_days_succeeds():
    order = _make_order(days_ago=29)
    service, refund_repo, _ = _make_service(order=order)

    result = service.request_refund(
        user_id=1, order_id=10, order_item_id=1, reason="damaged"
    )

    assert result.status == "requested"
    assert result.refund_amount == Decimal("200.00")
    refund_repo.create.assert_called_once()


def test_request_refund_after_30_days_returns_400():
    order = _make_order(days_ago=31)
    service, _, _ = _make_service(order=order)

    with pytest.raises(HTTPException) as exc_info:
        service.request_refund(user_id=1, order_id=10, order_item_id=1, reason=None)

    assert exc_info.value.status_code == 400


def test_request_refund_uses_discount_inclusive_amount():
    order = _make_order(days_ago=5)
    order.items[0].price = Decimal("80.00")
    order.items[0].quantity = 2

    service, refund_repo, _ = _make_service(order=order)
    service.request_refund(user_id=1, order_id=10, order_item_id=1, reason=None)

    args = refund_repo.create.call_args[0]
    assert args[3] == Decimal("160.00")


def test_request_refund_duplicate_returns_400():
    order = _make_order(days_ago=5)
    existing_request = MagicMock()
    service, _, _ = _make_service(order=order, active_request=existing_request)

    with pytest.raises(HTTPException) as exc_info:
        service.request_refund(user_id=1, order_id=10, order_item_id=1, reason=None)

    assert exc_info.value.status_code == 400
