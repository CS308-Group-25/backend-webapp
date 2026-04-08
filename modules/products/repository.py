from sqlalchemy.orm import Session

from modules.products.model import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Product]:
        return (
            self.db.query(Product)
            .filter(Product.deleted_at.is_(None))
            .all()
        )
    
    def get_by_id(self, product_id: int) -> Product | None:
        return (
            self.db.query(Product)
            .filter(Product.id == product_id, Product.deleted_at.is_(None))
            .first()
        )

    def create_product(self, product_data: dict) -> Product:
        db_product = Product(**product_data)
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        
        return db_product

    def update_stock(self, product_id: int, quantity: int) -> None:
        product = self.get_by_id(product_id)
        product.stock -= quantity
        self.db.commit()
