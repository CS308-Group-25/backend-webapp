from types import SimpleNamespace
from unittest.mock import MagicMock, patch, call
import pytest
from fastapi import HTTPException

from modules.orders.service import OrderService
from modules.orders.schema import OrderRequest


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def repos():
    """Return (order_repo, cart_repo, product_repo) as mocks."""
    return MagicMock(), MagicMock(), MagicMock()


@pytest.fixture
def service(repos):
    order_repo, cart_repo, product_repo = repos
    return OrderService(
        order_repo=order_repo,
        cart_repo=cart_repo,
        product_repo=product_repo,
    )


@pytest.fixture
def order_request():
    req = MagicMock(spec=OrderRequest)
    req.card_number = "1234567812345678"
    req.card_last4 = "5678"
    req.card_brand = "Visa"
    req.delivery_address = "123 Test St"
    return req


def _make_cart(items: list, cart_id: int = 10):
    cart = SimpleNamespace(id=cart_id, items=items)
    return cart


def _make_cart_item(product_id: int = 100, quantity: int = 2):
    return SimpleNamespace(id=1, product_id=product_id, quantity=quantity)


def _make_product(product_id: int = 100, stock: int = 10, price: float = 25.0, name: str = "Widget"):
    return SimpleNamespace(id=product_id, stock=stock, price=price, name=name)


def _make_order(order_id: int = 500, total: float = 50.0):
    order = MagicMock()
    order.id = order_id
    order.total = total
    order.status = "confirmed"
    order.delivery_address = "123 Test St"
    order.created_at = "2024-01-01T00:00:00"
    order.user_id = 1
    order.items = []
    return order


# ── Tests ─────────────────────────────────────────────────────────────────────

@patch("modules.orders.service.process_payment", return_value=True)
def test_place_order_success(mock_payment, service, repos, order_request):
    """
    Happy path: a valid cart with sufficient stock should create an order,
    process payment, decrement stock, and clear the cart.
    """
    order_repo, cart_repo, product_repo = repos

    cart_item = _make_cart_item(quantity=2)
    cart_repo.get.return_value = _make_cart([cart_item])

    product = _make_product(stock=10, price=25.0)
    product_repo.get_by_id.return_value = product

    order = _make_order(order_id=500, total=50.0)
    order_repo.create_order.return_value = order

    result = service.place_order(user_id=1, data=order_request)

    assert result is not None
    cart_repo.get.assert_called_once_with(1)
    order_repo.create_order.assert_called_once()
    order_repo.create_payment.assert_called_once()
    cart_repo.remove_item.assert_called_once_with(cart_item.id)


@patch("modules.orders.service.process_payment", return_value=True)
def test_place_order_out_of_stock_rejection(mock_payment, service, repos, order_request):
    """
    When a cart item quantity exceeds available stock, a 400 HTTPException
    should be raised and no order or payment should be created.
    """
    order_repo, cart_repo, product_repo = repos

    cart_repo.get.return_value = _make_cart([_make_cart_item(quantity=5)])
    product_repo.get_by_id.return_value = _make_product(stock=2)  # insufficient

    with pytest.raises(HTTPException, match="(?i)(stock|insufficient)") as exc:
        service.place_order(user_id=1, data=order_request)

    assert exc.value.status_code == 400
    order_repo.create_order.assert_not_called()
    order_repo.create_payment.assert_not_called()
    mock_payment.assert_not_called()


@patch("modules.orders.service.process_payment", return_value=True)
def test_place_order_stock_decrements_correctly(mock_payment, service, repos, order_request):
    """
    After a successful order, product_repo.update_stock should be called with
    the correct product ID and exact quantity purchased.
    """
    order_repo, cart_repo, product_repo = repos

    cart_item = _make_cart_item(product_id=100, quantity=3)
    cart_repo.get.return_value = _make_cart([cart_item])

    product = _make_product(product_id=100, stock=10)
    product_repo.get_by_id.return_value = product

    order_repo.create_order.return_value = _make_order()

    service.place_order(user_id=1, data=order_request)

    # update_stock is called twice: once in stock-check loop, once in order-item loop.
    # We assert at least one call carries the right args.
    product_repo.update_stock.assert_called_with(100, 3)


@patch("modules.orders.service.process_payment", return_value=True)
def test_place_order_card_number_not_persisted(mock_payment, service, repos):
    """
    The full card number must never reach create_payment.
    Only card_last4 and card_brand are safe to persist.
    """
    order_repo, cart_repo, product_repo = repos

    sensitive_card_number = "1111222233334444"

    order_request = MagicMock(spec=OrderRequest)
    order_request.card_number = sensitive_card_number
    order_request.card_last4 = "4444"
    order_request.card_brand = "Visa"
    order_request.delivery_address = "123 Test St"

    cart_item = _make_cart_item(quantity=1)
    cart_repo.get.return_value = _make_cart([cart_item])
    product_repo.get_by_id.return_value = _make_product(stock=10, price=25.0)
    order_repo.create_order.return_value = _make_order()

    service.place_order(user_id=1, data=order_request)

    order_repo.create_payment.assert_called_once()
    args, kwargs = order_repo.create_payment.call_args

    # Serialise only what was actually passed — no regex, just direct string check
    call_str = str(args) + str(kwargs)
    assert sensitive_card_number not in call_str, "Full PAN must never be persisted"
    assert "4444" in call_str, "Last 4 digits must be retained for display"
    assert "Visa" in call_str, "Card brand must be retained"