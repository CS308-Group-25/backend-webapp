from fastapi import HTTPException

from modules.products.model import Product
from modules.products.repository import ProductRepository
from modules.products.schema import ProductCreate, ProductUpdate
from modules.wishlist.notification_service import WishlistNotificationService


class ProductService:
    def __init__(
        self,
        repo: ProductRepository,
        notification_service: WishlistNotificationService | None = None,
    ):
        self.repo = repo
        # Optional: fires wishlist price-drop emails when a price update is detected
        self.notification_service = notification_service

    def list_products(
        self,
        search: str | None = None,
        sort: str | None = None,
        category_id: int | None = None,
        brand: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Product], int]:

        return self.repo.get_all(
            search=search,
            sort=sort,
            category_id=category_id,
            brand=brand,
            page=page,
            page_size=page_size,
        )

    def get_product(self, product_id: int) -> Product:
        product = self.repo.get_by_id(product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")

        return product

    def create_product(self, product_in: ProductCreate) -> Product:
        product_data = product_in.model_dump()

        return self.repo.create_product(product_data)

    def update_product(self, product_id: int, product_in: "ProductUpdate") -> Product:
        product = self.get_product(product_id)  # Raises 404 if not found

        # Capture old price before applying changes (needed for notification)
        old_price = float(product.price) if product.price is not None else None

        update_data = product_in.model_dump(exclude_unset=True)
        updated = self.repo.update_product(product, update_data)

        # Trigger wishlist email notifications if the price dropped
        new_price_raw = update_data.get("price")
        if (
            self.notification_service is not None
            and old_price is not None
            and new_price_raw is not None
        ):
            self.notification_service.notify_price_drop(
                product_id=product_id,
                product_name=updated.name,
                old_price=old_price,
                new_price=float(new_price_raw),
            )

        return updated

    def delete_product(self, product_id: int) -> None:
        product = self.get_product(product_id)
        self.repo.soft_delete_product(product)
