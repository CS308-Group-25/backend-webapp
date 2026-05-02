from datetime import datetime, timezone

from sqlalchemy.orm import Session

from modules.products.model import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        search: str | None = None,
        sort: str | None = None,
        category_id: int | None = None,
        brand: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Product], int]:
        query = self.db.query(Product).filter(Product.deleted_at.is_(None))

        if search:
            term = f"%{search}%"
            query = query.filter(
                Product.name.ilike(term) | Product.description.ilike(term)
            )

        if category_id is not None:
            query = query.filter(Product.category_id == category_id)

        if brand:
            query = query.filter(Product.brand.ilike(f"%{brand}%"))

        if sort == "price_asc":
            query = query.order_by(Product.price.asc())
        elif sort == "price_desc":
            query = query.order_by(Product.price.desc())
        elif sort == "popularity_desc":
            query = query.order_by(Product.stock.desc())
        elif sort == "newest":
            query = query.order_by(Product.created_at.desc())

        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()

        return items, total

    def get_by_id(self, product_id: int) -> Product | None:
        return (
            self.db.query(Product)
            .filter(Product.id == product_id, Product.deleted_at.is_(None))
            .first()
        )
    
    def get_by_id_for_update(self, product_id: int) -> Product | None:
        """
        Fetches a product and locks the row with SELECT FOR UPDATE.
        Use during order placement to prevent concurrent stock modifications.
        """
        return (
            self.db.query(Product)
            .filter(Product.id == product_id, Product.deleted_at.is_(None))
            .with_for_update()
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
        # Caller must hold a SELECT FOR UPDATE lock on this product 
        # (via get_by_id_for_update) before calling this.
        product = self.get_by_id(product_id)
        product.stock -= quantity
        # commit in calling service
