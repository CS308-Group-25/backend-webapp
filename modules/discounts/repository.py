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
