import logging

from core.discount_email import send_wishlist_discount_email
from modules.wishlist.repository import WishlistRepository

logger = logging.getLogger(__name__)


class WishlistNotificationService:
    """Sends discount alert emails to users who have wishlisted a product."""

    def __init__(self, wishlist_repo: WishlistRepository):
        self.wishlist_repo = wishlist_repo

    def notify_price_drop(
        self,
        product_id: int,
        product_name: str,
        old_price: float,
        new_price: float,
    ) -> None:
        """Email every user who has wishlisted the product about the price drop.

        Only sends notifications when new_price is strictly lower than old_price.
        Failures for individual recipients are logged but do not abort the loop,
        so one bad address cannot block notifications to other users.

        Args:
            product_id: ID of the discounted product.
            product_name: Display name used in the email subject/body.
            old_price: Price before the discount was applied.
            new_price: Price after the discount was applied.
        """
        # Only trigger when the price actually went down
        if new_price >= old_price:
            return

        users = self.wishlist_repo.get_users_by_product(product_id)
        if not users:
            return

        for user in users:
            try:
                send_wishlist_discount_email(
                    to_email=user.email,
                    user_name=user.name,
                    product_name=product_name,
                    old_price=old_price,
                    new_price=new_price,
                )
                logger.info(
                    "Discount notification sent to %s for product %s",
                    user.email,
                    product_id,
                )
            except Exception:
                # Log and continue — one failed delivery should not block the rest
                logger.exception(
                    "Failed to send discount notification to %s for product %s",
                    user.email,
                    product_id,
                )
