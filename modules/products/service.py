from decimal import Decimal

from fastapi import HTTPException

from modules.discounts.repository import DiscountRepository
from modules.products.model import Product
from modules.products.repository import ProductRepository
from modules.products.schema import ProductCreate, ProductUpdate
from modules.wishlist.notification_service import WishlistNotificationService


class ProductService:
    def __init__(
        self,
        repo: ProductRepository,
        notification_service: WishlistNotificationService | None = None,
        discount_repo: DiscountRepository | None = None,
    ):
        self.repo = repo
        self.notification_service = notification_service
        self.discount_repo = discount_repo

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


    def set_price(self, product_id: int, price: Decimal) -> Product:
        product = self.get_product(product_id)

        # Keep every active discount's stored original in sync with the new base
        # price. Without this, remove_discount() would restore the stale
        # pre-sales-manager value and silently overwrite this update.
        if self.discount_repo is not None:
            for discount in self.discount_repo.get_by_product_id(product_id):
                updated = dict(discount.original_prices)
                updated[str(product_id)] = str(price)
                self.discount_repo.update_original_prices(discount, updated)

        update_data: dict = {"price": price}

        sizes = product.sizes_json
        if sizes:
            ref_raw = sizes[0].get("price") if isinstance(sizes[0], dict) else None
            ref = Decimal(str(ref_raw)) if ref_raw else None
            updated_sizes = []
            for size in sizes:
                if not isinstance(size, dict) or size.get("price") is None:
                    updated_sizes.append(size)
                    continue
                if ref:
                    scaled = Decimal(str(size["price"])) * price / ref
                    new_size_price = scaled.quantize(Decimal("0.01"))
                else:
                    # sizes[0].price is None or 0 — set every size to new price
                    new_size_price = price.quantize(Decimal("0.01"))
                updated_sizes.append({**size, "price": float(new_size_price)})
            update_data["sizes_json"] = updated_sizes

        return self.repo.update_product(product, update_data)
