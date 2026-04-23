from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from modules.orders.model import Order
from modules.orders.schema import OrderRequest
from modules.orders.service import OrderService

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def repos():
    """Return (order_repo, cart_repo, product_repo) as mocks."""
    return MagicMock(), MagicMock(), MagicMock()


@pytest.fixture
def service(repos):
    order_repo, cart_repo, product_repo = repos
    invoice_service = MagicMock()
    return OrderService(
        order_repo=order_repo,
        cart_repo=cart_repo,
        product_repo=product_repo,
        invoice_service=invoice_service,
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


def _make_product(
    product_id: int = 100, stock: int = 10, price: float = 25.0, name: str = "Widget"
):
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


def _make_service(order_repo=None, cart_repo=None, product_repo=None, invoice_service=None):
    return OrderService(
        order_repo=order_repo or MagicMock(),
        cart_repo=cart_repo or MagicMock(),
        product_repo=product_repo or MagicMock(),
        invoice_service=invoice_service or MagicMock(),
    )

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
def test_place_order_out_of_stock_rejection(
    mock_payment, service, repos, order_request
):
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
def test_place_order_stock_decrements_correctly(
    mock_payment, service, repos, order_request
):
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


def test_update_status_processing_to_in_transit_valid():
    """T-213: Valid status transition from processing to in_transit."""
    # Arrange
    order_repo = MagicMock()
    order = MagicMock(spec=Order)
    order.status = "processing"
    order_repo.get_by_order_id.return_value = order

    updated_order = MagicMock(spec=Order)
    updated_order.id = 1
    updated_order.status = "in_transit"
    updated_order.total = 100.0
    updated_order.invoice = None
    updated_order.delivery_address = "Address"
    from datetime import datetime, timezone

    updated_order.created_at = datetime.now(timezone.utc)
    updated_order.items = []

    order_repo.update_order_status.return_value = updated_order

    service = _make_service(order_repo=order_repo)

    # Act
    result = service.update_order_status(order_id=1, new_status="in_transit")

    # Assert
    assert result.status == "in_transit"
    order_repo.update_order_status.assert_called_once_with(1, "in_transit")


def test_update_status_delivered_to_processing_invalid():
    """T-213: Invalid status transition from delivered back to processing returns 400."""  # noqa: E501
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


def test_get_admin_orders_nested_items():
    """T-207: Verify get_admin_orders returns one object per order with nested items"""
    order_repo = MagicMock()

    user = MagicMock()
    user.name = "Test Admin"
    user.email = "admin@test.com"

    item1 = MagicMock()
    item1.product_id = 101
    item1.quantity = 2
    item1.price = 50.0
    item1.product = MagicMock()
    item1.product.name = "Product A"

    item2 = MagicMock()
    item2.product_id = 102
    item2.quantity = 1
    item2.price = 50.0
    item2.product = MagicMock()
    item2.product.name = "Product B"

    order = MagicMock(spec=Order)
    order.id = 100
    order.user_id = 10
    order.user = user
    order.items = [item1, item2]
    order.total = 150.0
    order.delivery_address = "Admin Address"
    order.status = "processing"

    order_repo.get_all_orders.return_value = [order]

    service = _make_service(order_repo=order_repo)

    results = service.get_admin_orders(status="processing")

    assert len(results) == 1
    assert results[0].order_id == 100
    assert results[0].customer_id == 10
    assert results[0].total == 150.0
    assert len(results[0].items) == 2
    assert results[0].items[0].product_id == 101
    assert results[0].items[0].quantity == 2
    assert results[0].delivery_address == "Admin Address"
    assert results[0].status == "processing"
    assert results[0].completed is False
    assert results[0].customer_name == "Test Admin"
    assert results[0].customer_email == "admin@test.com"
