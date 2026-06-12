from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from modules.auth.model import User
from modules.discounts.service import DiscountService
from modules.products.model import Product


def _make_service():
    discount_repo = MagicMock()
    product_repo = MagicMock()
    wishlist_repo = MagicMock()
    svc = DiscountService(discount_repo, product_repo, wishlist_repo)
    return svc, discount_repo, product_repo, wishlist_repo


def test_apply_discount_recalculates_prices():
    service, discount_repo, product_repo, wishlist_repo = _make_service()

    product = Product(id=1, name="Whey Protein", price=Decimal("100.00"), stock=50)
    product_repo.get_by_id.return_value = product
    discount_repo.create_discount.return_value = MagicMock()
    wishlist_repo.get_users_by_product.return_value = []

    service.apply_discount(product_ids=[1], discount_rate=Decimal("20"), created_by=99)

    product_repo.update_product.assert_called_once_with(
        product, {"original_price": Decimal("100.00"), "price": Decimal("80.00")}
    )


def test_apply_discount_rejects_already_discounted_product():
    service, _, product_repo, _ = _make_service()

    product = Product(
        id=1, name="Whey Protein",
        price=Decimal("80.00"), original_price=Decimal("100.00"), stock=50,
    )
    product_repo.get_by_id.return_value = product

    with pytest.raises(HTTPException) as exc_info:
        service.apply_discount(
            product_ids=[1], discount_rate=Decimal("10"), created_by=99
        )

    assert exc_info.value.status_code == 400


def test_remove_discount_restores_original_prices():
    service, discount_repo, product_repo, _ = _make_service()

    mock_discount = MagicMock()
    mock_discount.original_prices = {"1": "99.99"}
    discount_repo.get_by_id.return_value = mock_discount

    # product.original_price is None — falls back to discount record snapshot
    product = Product(id=1, name="Whey Protein", price=Decimal("79.99"), stock=50)
    product_repo.get_by_id.return_value = product

    service.remove_discount(discount_id=1)

    product_repo.update_product.assert_called_once_with(
        product, {"price": Decimal("99.99"), "original_price": None}
    )
    discount_repo.delete_discount.assert_called_once_with(mock_discount)


def test_remove_discount_uses_product_original_price_when_set():
    service, discount_repo, product_repo, _ = _make_service()

    mock_discount = MagicMock()
    mock_discount.original_prices = {"1": "99.99"}  # stale — should be ignored
    discount_repo.get_by_id.return_value = mock_discount

    # product.original_price is set — takes priority over the discount record
    product = Product(
        id=1, name="Whey Protein",
        price=Decimal("79.99"), original_price=Decimal("120.00"), stock=50,
    )
    product_repo.get_by_id.return_value = product

    service.remove_discount(discount_id=1)

    product_repo.update_product.assert_called_once_with(
        product, {"price": Decimal("120.00"), "original_price": None}
    )


def test_apply_discount_triggers_wishlist_notification():
    discount_repo = MagicMock()
    product_repo = MagicMock()
    wishlist_repo = MagicMock()
    notif_repo = MagicMock()
    service = DiscountService(discount_repo, product_repo, wishlist_repo, notif_repo)

    product = Product(id=1, name="Whey Protein", price=Decimal("100.00"), stock=50)
    product_repo.get_by_id.return_value = product
    discount_repo.create_discount.return_value = MagicMock()

    wishlisted_user = User(
        id=5, name="Ali Veli", email="ali@example.com", role="customer"
    )
    wishlist_repo.get_users_by_product.return_value = [wishlisted_user]

    service.apply_discount(
        product_ids=[1],
        discount_rate=Decimal("20"),
        created_by=99,
    )

    notif_repo.create.assert_called_once_with(
        5,
        "Favori listenizde bulunan 'Whey Protein' "
        "ürününde %20 indirim! "
        "100.00 TL → 80.00 TL",
    )
