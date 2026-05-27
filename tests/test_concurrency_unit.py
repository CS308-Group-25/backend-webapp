from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from modules.orders.schema import OrderRequest
from modules.orders.service import OrderService

# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_cart_item(product_id: int = 100, quantity: int = 1):
    return SimpleNamespace(
        id=1, product_id=product_id, quantity=quantity, variant_name=None
    )


def _make_cart(items: list, cart_id: int = 10):
    return SimpleNamespace(id=cart_id, items=items)


def _make_product(
    product_id: int = 100, stock: int = 5, price: float = 20.0, name: str = "Item"
):
    return SimpleNamespace(id=product_id, stock=stock, price=price, name=name)


def _make_order(order_id: int = 500, total: float = 20.0):
    order = MagicMock()
    order.id = order_id
    order.total = total
    order.status = "confirmed"
    order.delivery_address = "1 Test Rd"
    order.created_at = "2024-01-01T00:00:00"
    order.user_id = 1
    order.items = []
    return order


def _make_order_request():
    req = MagicMock(spec=OrderRequest)
    req.card_number = "4111111111111111"
    req.card_last4 = "1111"
    req.card_brand = "Visa"
    req.delivery_address = "1 Test Rd"
    return req


def _make_service(
    order_repo=None, cart_repo=None, product_repo=None, invoice_service=None
):
    return OrderService(
        order_repo=order_repo or MagicMock(),
        cart_repo=cart_repo or MagicMock(),
        product_repo=product_repo or MagicMock(),
        invoice_service=invoice_service or MagicMock(),
    )


# ── Tests ─────────────────────────────────────────────────────────────────────


@patch("modules.orders.service.send_invoice_email")
@patch("modules.orders.service.process_payment", return_value=True)
def test_concurrent_last_item_first_caller_succeeds_second_gets_409(
    mock_payment, mock_email
):
    """
    T-238a: Two concurrent checkouts compete for the last item in stock.
    The first caller acquires the row lock, commits, and succeeds.
    The second caller's pre-payment check read a stale stock=1, but the
    SELECT FOR UPDATE re-check inside the transaction sees stock=0 and
    raises 409 Conflict, preventing an oversell.
    """
    # First caller — stock=1, qty=1, lock confirms availability, succeeds.
    order_repo_a = MagicMock()
    cart_repo_a = MagicMock()
    product_repo_a = MagicMock()
    cart_repo_a.get.return_value = _make_cart(
        [_make_cart_item(product_id=77, quantity=1)]
    )
    last_item = _make_product(product_id=77, stock=1)
    product_repo_a.get_by_id.return_value = last_item
    product_repo_a.get_by_id_for_update.return_value = last_item
    order_repo_a.create_order.return_value = _make_order()

    result = _make_service(order_repo_a, cart_repo_a, product_repo_a).place_order(
        user_id=1, data=_make_order_request()
    )

    assert result is not None
    product_repo_a.update_stock.assert_called_once_with(77, 1)
    order_repo_a.db.commit.assert_called_once()

    # Second caller: stale pre-check (stock=1), locked re-check sees stock=0.
    order_repo_b = MagicMock()
    cart_repo_b = MagicMock()
    product_repo_b = MagicMock()
    cart_repo_b.get.return_value = _make_cart(
        [_make_cart_item(product_id=77, quantity=1)]
    )
    product_repo_b.get_by_id.return_value = _make_product(product_id=77, stock=1)
    product_repo_b.get_by_id_for_update.return_value = _make_product(
        product_id=77, stock=0
    )

    with pytest.raises(HTTPException) as exc:
        _make_service(order_repo_b, cart_repo_b, product_repo_b).place_order(
            user_id=2, data=_make_order_request()
        )

    assert exc.value.status_code == 409
    order_repo_b.create_order.assert_not_called()
    order_repo_b.create_payment.assert_not_called()
    order_repo_b.db.rollback.assert_called_once()
    order_repo_b.db.commit.assert_not_called()


@patch("modules.orders.service.process_payment", return_value=True)
def test_oversell_prevented_by_locked_recheck(mock_payment):
    """
    T-238b: SELECT FOR UPDATE re-validation blocks an oversell.
    The pre-payment stock check passes (stock=5, qty=3), but another
    concurrent transaction has since decremented stock to 2. The locked
    re-check detects the shortfall and raises 409 before any order or stock
    change is written, ensuring no partial state exists in the database.
    """
    order_repo = MagicMock()
    cart_repo = MagicMock()
    product_repo = MagicMock()

    cart_repo.get.return_value = _make_cart(
        [_make_cart_item(product_id=55, quantity=3)]
    )
    product_repo.get_by_id.return_value = _make_product(product_id=55, stock=5)
    product_repo.get_by_id_for_update.return_value = _make_product(
        product_id=55, stock=2
    )

    with pytest.raises(HTTPException) as exc:
        _make_service(order_repo, cart_repo, product_repo).place_order(
            user_id=1, data=_make_order_request()
        )

    assert exc.value.status_code == 409
    order_repo.create_order.assert_not_called()
    product_repo.update_stock.assert_not_called()
    order_repo.db.rollback.assert_called_once()
    order_repo.db.commit.assert_not_called()


@patch("modules.orders.service.process_payment", return_value=True)
def test_transaction_rolls_back_on_unexpected_failure_during_order_creation(
    mock_payment,
):
    """
    T-238c: If an unexpected error occurs inside the atomic block (e.g. a
    database error at create_order time), the service rolls back the
    transaction, skips the stock decrement, and raises HTTP 500 so that
    the database is never left in a partial order state.
    """
    order_repo = MagicMock()
    cart_repo = MagicMock()
    product_repo = MagicMock()

    cart_repo.get.return_value = _make_cart(
        [_make_cart_item(product_id=33, quantity=2)]
    )
    product_repo.get_by_id.return_value = _make_product(product_id=33, stock=10)
    product_repo.get_by_id_for_update.return_value = _make_product(
        product_id=33, stock=10
    )
    order_repo.create_order.side_effect = Exception("DB connection lost")

    with pytest.raises(HTTPException) as exc:
        _make_service(order_repo, cart_repo, product_repo).place_order(
            user_id=1, data=_make_order_request()
        )

    assert exc.value.status_code == 500
    order_repo.db.rollback.assert_called_once()
    order_repo.db.commit.assert_not_called()
    product_repo.update_stock.assert_not_called()
    order_repo.create_payment.assert_not_called()
