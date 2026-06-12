from decimal import Decimal

from fastapi import HTTPException

from modules.discounts.model import Discount
from modules.discounts.repository import DiscountRepository
from modules.notifications.repository import NotificationRepository
from modules.products.repository import ProductRepository
from modules.wishlist.repository import WishlistRepository


class DiscountService:
    def __init__(
        self,
        discount_repo: DiscountRepository,
        product_repo: ProductRepository,
        wishlist_repo: WishlistRepository,
        notif_repo: NotificationRepository | None = None,
    ):
        self.discount_repo = discount_repo
        self.product_repo = product_repo
        self.wishlist_repo = wishlist_repo
        self.notif_repo = notif_repo

    def list_discounts(self) -> list[Discount]:
        return self.discount_repo.get_all()

    def apply_discount(
        self,
        product_ids: list[int],
        discount_rate: Decimal,
        created_by: int,
    ) -> Discount:
        discount_rate = Decimal(str(discount_rate))

        # Fetch and validate all products before touching anything
        products = []
        for pid in product_ids:
            product = self.product_repo.get_by_id(pid)
            if product is None:
                raise HTTPException(status_code=404, detail=f"Product {pid} not found")
            if product.price is None:
                raise HTTPException(
                    status_code=400, detail=f"Product {pid} has no base price set"
                )
            if product.original_price is not None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Product {pid} already has an active discount",
                )
            products.append(product)

        # Snapshot prices now — create_discount commits and expires ORM objects
        original_prices = {str(p.id): str(p.price) for p in products}

        discount = self.discount_repo.create_discount({
            "product_ids": product_ids,
            "discount_rate": discount_rate,
            "original_prices": original_prices,
            "created_by": created_by,
        })

        new_prices = {}
        multiplier = (Decimal(100) - discount_rate) / Decimal(100)
        for product in products:
            # Read price BEFORE writing original_price — avoids stale reads if
            # the ORM flushes between attribute assignments on an expired object.
            original = Decimal(str(product.price))
            new_price = (original * multiplier).quantize(Decimal("0.01"))
            new_prices[product.id] = new_price

            update_data: dict = {"original_price": original, "price": new_price}
            sizes = product.sizes_json
            if sizes:
                updated_sizes = []
                for size in sizes:
                    if isinstance(size, dict) and size.get("price") is not None:
                        scaled = (Decimal(str(size["price"])) * multiplier).quantize(
                            Decimal("0.01")
                        )
                        updated_sizes.append({**size, "price": float(scaled)})
                    else:
                        updated_sizes.append(size)
                update_data["sizes_json"] = updated_sizes
            self.product_repo.update_product(product, update_data)

        if self.notif_repo:
            for product in products:
                old_price_f = float(original_prices[str(product.id)])
                new_price_f = float(new_prices[product.id])
                for user in self.wishlist_repo.get_users_by_product(product.id):
                    self.notif_repo.create(
                        user.id,
                        f"Favori listenizde bulunan '{product.name}' ürününde %{int(discount_rate)} indirim! "
                        f"{old_price_f:.2f} TL → {new_price_f:.2f} TL",
                    )
            self.discount_repo.db.commit()

        return discount

    def remove_discount(self, discount_id: int) -> None:
        discount = self.discount_repo.get_by_id(discount_id)
        if discount is None:
            raise HTTPException(status_code=404, detail="Discount not found")

        # Restore original prices before deleting the record.
        # Prefer product.original_price (set since this fix); fall back to the
        # JSON snapshot in the discount row for discounts created before the fix.
        for str_pid, str_price in discount.original_prices.items():
            product = self.product_repo.get_by_id(int(str_pid))
            if product is None:
                continue  # product was soft-deleted; nothing to restore
            restore_to = (
                product.original_price
                if product.original_price is not None
                else Decimal(str_price)
            )
            update_data: dict = {"price": restore_to, "original_price": None}
            sizes = product.sizes_json
            if sizes:
                ref_raw = sizes[0].get("price") if isinstance(sizes[0], dict) else None
                ref = Decimal(str(ref_raw)) if ref_raw else None
                if ref:
                    ratio = restore_to / ref
                    updated_sizes = []
                    for size in sizes:
                        if isinstance(size, dict) and size.get("price") is not None:
                            restored = (
                                Decimal(str(size["price"])) * ratio
                            ).quantize(Decimal("0.01"))
                            updated_sizes.append({**size, "price": float(restored)})
                        else:
                            updated_sizes.append(size)
                    update_data["sizes_json"] = updated_sizes
            self.product_repo.update_product(product, update_data)

        self.discount_repo.delete_discount(discount)
