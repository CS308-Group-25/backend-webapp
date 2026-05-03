from decimal import Decimal

from fastapi import HTTPException

from modules.discounts.model import Discount
from modules.discounts.repository import DiscountRepository
from modules.products.repository import ProductRepository


class DiscountService:
    def __init__(self, 
                discount_repo: DiscountRepository, 
                product_repo: ProductRepository):
        self.discount_repo = discount_repo
        self.product_repo = product_repo

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

        multiplier = (Decimal(100) - discount_rate) / Decimal(100) 
        for product in products:
            new_price = (Decimal(str(product.price)) * multiplier).quantize(Decimal("0.01"))    # noqa: E501 
            self.product_repo.update_product(product, {"price": new_price})

        return discount
