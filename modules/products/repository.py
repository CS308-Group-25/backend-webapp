from sqlalchemy.orm import Session

from modules.products.model import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_product(self, product_data: dict) -> Product:
        db_product = Product(**product_data)
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def get_by_id(self, product_id: int) -> Product | None:
        return self.db.query(Product).filter(Product.id == product_id).first()