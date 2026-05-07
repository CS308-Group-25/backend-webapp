from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import set_committed_value

from modules.products.model import Product
from modules.reviews.model import Review


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
        self._attach_review_stats(items)

        return items, total

    def get_by_id(self, product_id: int) -> Product | None:
        product = (
            self.db.query(Product)
            .filter(Product.id == product_id, Product.deleted_at.is_(None))
            .first()
        )
        if product is not None:
            self._attach_review_stats([product])
        return product

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
        # Use a direct SQL UPDATE to guarantee the change is written to the DB row.
        # GREATEST(..., 0) is a safety net to prevent stock from going negative.
        from sqlalchemy import text

        self.db.execute(
            text(
                "UPDATE products SET stock = GREATEST(stock - :qty, 0) WHERE id = :pid"
            ),
            {"qty": quantity, "pid": product_id},
        )
        # commit in calling service

    def increment_stock(self, product_id: int, quantity: int) -> None:
        # Inverse of update_stock (decrement). Used for refunds/cancellations.
        from sqlalchemy import text

        self.db.execute(
            text("UPDATE products SET stock = stock + :qty WHERE id = :pid"),
            {"qty": quantity, "pid": product_id},
        )
        # commit in calling service

    def _attach_review_stats(self, products: list[Product]) -> None:
        product_ids = [product.id for product in products]
        if not product_ids:
            return

        rating_stats = (
            self.db.query(
                Review.product_id,
                func.avg(Review.rating).label("average_rating"),
                func.count(Review.id).label("rating_count"),
            )
            .filter(Review.product_id.in_(product_ids))
            .filter(Review.rating.is_not(None))
            .group_by(Review.product_id)
            .all()
        )
        comment_stats = (
            self.db.query(
                Review.product_id,
                func.count(Review.id).label("comment_count"),
            )
            .filter(Review.product_id.in_(product_ids))
            .filter(Review.approval_status == "approved")
            .filter(Review.comment.is_not(None))
            .group_by(Review.product_id)
            .all()
        )

        rating_stats_by_product_id = {
            product_id: (average_rating, rating_count)
            for product_id, average_rating, rating_count in rating_stats
        }
        comment_counts_by_product_id = {
            product_id: comment_count for product_id, comment_count in comment_stats
        }

        for product in products:
            average_rating, rating_count = rating_stats_by_product_id.get(
                product.id,
                (0, 0),
            )
            rounded_rating = Decimal(str(round(float(average_rating or 0), 2)))
            set_committed_value(product, "rating", rounded_rating)
            set_committed_value(product, "review_count", int(rating_count or 0))
            product.comment_count = int(comment_counts_by_product_id.get(product.id, 0))
