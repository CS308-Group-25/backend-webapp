from datetime import datetime, timezone

from sqlalchemy.orm import Session

from modules.products.model import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, search: str | None = None, sort: str | None = None,
                ) -> list[Product]:
        query = self.db.query(Product).filter(Product.deleted_at.is_(None))

        if search:
            term = f"%{search}%"
            query = query.filter(
                Product.name.ilike(term) | Product.description.ilike(term))

        return query.all()
    
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
        db_product.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product
    
    def update_stock(self, product_id: int, quantity: int) -> None:
        product = self.get_by_id(product_id)
        product.stock -= quantity
        self.db.commit()
