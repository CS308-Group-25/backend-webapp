import logging
from decimal import Decimal

from fastapi import HTTPException

from core.discount_email import send_wishlist_discount_email
from modules.discounts.model import Discount
from modules.discounts.repository import DiscountRepository
from modules.products.repository import ProductRepository
from modules.wishlist.repository import WishlistRepository

logger = logging.getLogger(__name__)


class DiscountService:
    def __init__(
        self,
        discount_repo: DiscountRepository,
        product_repo: ProductRepository,
        wishlist_repo: WishlistRepository,
    ):
        self.discount_repo = discount_repo
        self.product_repo = product_repo
        self.wishlist_repo = wishlist_repo

    def apply_discount(
        self,
        product_ids: list[int],
        discount_rate: Decimal,
        created_by: int,
    ) -> Discount:
        discount_rate = Decimal(str(discount_rate))

        # Fetch and validate all products before touching anything
        products = []
        for pid in product_ids:
            product = self.product_repo.get_by_id(pid)
            if product is None:
                raise HTTPException(status_code=404, detail=f"Product {pid} not found")
            if product.price is None:
                raise HTTPException(
                    status_code=400, detail=f"Product {pid} has no base price set"
                )
            products.append(product)

        # Persist original prices before overwriting — never recalculate on restore
        original_prices = {str(p.id): str(p.price) for p in products}

        discount = self.discount_repo.create_discount({
            "product_ids": product_ids,
            "discount_rate": discount_rate,
            "original_prices": original_prices,
            "created_by": created_by,
        })

        new_prices = {}
        multiplier = (Decimal(100) - discount_rate) / Decimal(100)
        for product in products:
            new_price = (
                Decimal(str(product.price)) * multiplier).quantize(Decimal("0.01"))
            new_prices[product.id] = new_price
            self.product_repo.update_product(product, {"price": new_price})

        for product in products:
            old_price_f = float(original_prices[str(product.id)])
            new_price_f = float(new_prices[product.id])
            for user in self.wishlist_repo.get_users_by_product(product.id):
                try:
                    send_wishlist_discount_email(
                        to_email=user.email,
                        user_name=user.name,
                        product_name=product.name,
                        old_price=old_price_f,
                        new_price=new_price_f,
                    )
                except Exception:
                    logger.warning(
                        "Failed to send discount notification to %s for product %d",
                        user.email,
                        product.id,
                    )

        return discount

    def remove_discount(self, discount_id: int) -> None:
        discount = self.discount_repo.get_by_id(discount_id)
        if discount is None:
            raise HTTPException(status_code=404, detail="Discount not found")

        # Restore original prices before deleting the record
        for str_pid, str_price in discount.original_prices.items():
            product = self.product_repo.get_by_id(int(str_pid))
            if product is None:
                continue  # product was soft-deleted; nothing to restore
            self.product_repo.update_product(product, {"price": Decimal(str_price)})

        self.discount_repo.delete_discount(discount)
