from sqlalchemy.orm import Session

from modules.discounts.model import Discount


class DiscountRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_discount(self, data: dict) -> Discount:
        discount = Discount(**data)
        self.db.add(discount)
        self.db.commit()
        self.db.refresh(discount)
        return discount

    def get_by_id(self, discount_id: int) -> Discount | None:
        return self.db.query(Discount).filter(Discount.id == discount_id).first()

    def get_by_product_id(self, product_id: int) -> list[Discount]:
        return [
            d for d in self.db.query(Discount).all()
            if product_id in (d.product_ids or [])
        ]

    def update_original_prices(self, discount: Discount, original_prices: dict) -> None:
        discount.original_prices = original_prices
        self.db.commit()

    def delete_discount(self, discount: Discount) -> None:
        self.db.delete(discount)
        self.db.commit()
