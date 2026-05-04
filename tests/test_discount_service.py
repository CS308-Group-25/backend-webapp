from decimal import Decimal
from unittest.mock import MagicMock, patch

from modules.auth.model import User
from modules.discounts.service import DiscountService
from modules.products.model import Product


def test_apply_discount_recalculates_prices():
    discount_repo = MagicMock()
    product_repo = MagicMock()
    wishlist_repo = MagicMock()
    service = DiscountService(discount_repo, product_repo, wishlist_repo)

    product = Product(id=1, name="Whey Protein", price=Decimal("100.00"), stock=50)
    product_repo.get_by_id.return_value = product
    discount_repo.create_discount.return_value = MagicMock()
    wishlist_repo.get_users_by_product.return_value = []

    service.apply_discount(
        product_ids=[1],
        discount_rate=Decimal("20"),
        created_by=99,
    )

    product_repo.update_product.assert_called_once_with(
        product, {"price": Decimal("80.00")}
    )


def test_remove_discount_restores_original_prices():
    discount_repo = MagicMock()
    product_repo = MagicMock()
    wishlist_repo = MagicMock()
    service = DiscountService(discount_repo, product_repo, wishlist_repo)

    mock_discount = MagicMock()
    mock_discount.original_prices = {"1": "99.99"}
    discount_repo.get_by_id.return_value = mock_discount

    product = Product(id=1, name="Whey Protein", price=Decimal("79.99"), stock=50)
    product_repo.get_by_id.return_value = product

    service.remove_discount(discount_id=1)

    product_repo.update_product.assert_called_once_with(
        product, {"price": Decimal("99.99")}
    )
    discount_repo.delete_discount.assert_called_once_with(mock_discount)


def test_apply_discount_triggers_wishlist_notification():
    discount_repo = MagicMock()
    product_repo = MagicMock()
    wishlist_repo = MagicMock()
    service = DiscountService(discount_repo, product_repo, wishlist_repo)

    product = Product(id=1, name="Whey Protein", price=Decimal("100.00"), stock=50)
    product_repo.get_by_id.return_value = product
    discount_repo.create_discount.return_value = MagicMock()

    wishlisted_user = User(
        id=5, name="Ali Veli", email="ali@example.com", role="customer"
    )
    wishlist_repo.get_users_by_product.return_value = [wishlisted_user]

    with patch("modules.discounts.service.send_wishlist_discount_email") as mock_email:
        service.apply_discount(
            product_ids=[1],
            discount_rate=Decimal("20"),
            created_by=99,
        )

    mock_email.assert_called_once_with(
        to_email="ali@example.com",
        user_name="Ali Veli",
        product_name="Whey Protein",
        old_price=100.0,
        new_price=80.0,
    )
