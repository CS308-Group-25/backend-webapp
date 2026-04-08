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

    def update_product(self, db_product: Product, update_data: dict) -> Product:
        for key, value in update_data.items():
            setattr(db_product, key, value)
        
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def soft_delete_product(self, db_product: Product) -> Product:
        # Avoid circular import by using datetime locally or importing at the top.
        # Actually func.now() will work best.
        from sqlalchemy.sql import func
        db_product.deleted_at = func.now()
        self.db.commit()
        self.db.refresh(db_product)
        return db_product
