"""Unit tests for T-232: wishlist discount notification system.

Tests cover:
  - WishlistNotificationService.notify_price_drop triggers email for each user
  - No email sent when new_price >= old_price
  - No email sent when nobody has the product wishlisted
  - A failed email for one user does not stop notifications to others
  - send_wishlist_discount_email builds correct subject and recipients
"""

from unittest.mock import MagicMock, patch

from modules.auth.model import User
from modules.wishlist.notification_service import WishlistNotificationService

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_user(user_id: int, name: str, email: str) -> User:
    user = User()
    user.id = user_id
    user.name = name
    user.email = email
    return user


# ---------------------------------------------------------------------------
# WishlistNotificationService tests
# ---------------------------------------------------------------------------

class TestWishlistNotificationService:
    """Tests for WishlistNotificationService.notify_price_drop."""

    def _make_service(self, users: list[User]) -> WishlistNotificationService:
        """Build service with a mock repo that returns the given users."""
        mock_repo = MagicMock()
        mock_repo.get_users_by_product.return_value = users
        return WishlistNotificationService(mock_repo)

    @patch("modules.wishlist.notification_service.send_wishlist_discount_email")
    def test_sends_email_to_each_wishlisting_user(self, mock_send):
        """Email is sent once per user who has the product wishlisted."""
        users = [
            _make_user(1, "Alice", "alice@example.com"),
            _make_user(2, "Bob", "bob@example.com"),
        ]
        service = self._make_service(users)

        service.notify_price_drop(
            product_id=10,
            product_name="Whey Protein",
            old_price=200.0,
            new_price=150.0,
        )

        assert mock_send.call_count == 2
        mock_send.assert_any_call(
            to_email="alice@example.com",
            user_name="Alice",
            product_name="Whey Protein",
            old_price=200.0,
            new_price=150.0,
        )
        mock_send.assert_any_call(
            to_email="bob@example.com",
            user_name="Bob",
            product_name="Whey Protein",
            old_price=200.0,
            new_price=150.0,
        )

    @patch("modules.wishlist.notification_service.send_wishlist_discount_email")
    def test_no_email_when_price_increases(self, mock_send):
        """No email sent when new price is higher than old price."""
        users = [_make_user(1, "Alice", "alice@example.com")]
        service = self._make_service(users)

        service.notify_price_drop(
            product_id=10,
            product_name="Whey Protein",
            old_price=150.0,
            new_price=200.0,  # price went UP
        )

        mock_send.assert_not_called()

    @patch("modules.wishlist.notification_service.send_wishlist_discount_email")
    def test_no_email_when_price_unchanged(self, mock_send):
        """No email sent when price does not change."""
        users = [_make_user(1, "Alice", "alice@example.com")]
        service = self._make_service(users)

        service.notify_price_drop(
            product_id=10,
            product_name="Whey Protein",
            old_price=150.0,
            new_price=150.0,  # same price
        )

        mock_send.assert_not_called()

    @patch("modules.wishlist.notification_service.send_wishlist_discount_email")
    def test_no_email_when_no_users_wishlisted(self, mock_send):
        """No email sent when nobody has the product wishlisted."""
        service = self._make_service([])

        service.notify_price_drop(
            product_id=10,
            product_name="Whey Protein",
            old_price=200.0,
            new_price=150.0,
        )

        mock_send.assert_not_called()

    @patch("modules.wishlist.notification_service.send_wishlist_discount_email")
    def test_one_failure_does_not_block_other_emails(self, mock_send):
        """If sending fails for one user, others still receive their emails."""
        users = [
            _make_user(1, "Alice", "alice@example.com"),
            _make_user(2, "Bob", "bob@example.com"),
            _make_user(3, "Carol", "carol@example.com"),
        ]
        # Alice's email raises an SMTP error
        mock_send.side_effect = [Exception("SMTP error"), None, None]

        service = self._make_service(users)

        # Should not raise — failures are caught internally
        service.notify_price_drop(
            product_id=10,
            product_name="Whey Protein",
            old_price=200.0,
            new_price=150.0,
        )

        # All three were attempted despite Alice's failure
        assert mock_send.call_count == 3


# ---------------------------------------------------------------------------
# send_wishlist_discount_email integration (SMTP mocked)
# ---------------------------------------------------------------------------

class TestSendWishlistDiscountEmail:
    """Tests for the email builder / SMTP sender."""

    @patch("core.discount_email.smtplib.SMTP")
    def test_email_sent_to_correct_recipient(self, mock_smtp_cls):
        """The email is addressed to the given recipient."""
        from core.discount_email import send_wishlist_discount_email

        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__.return_value = mock_server

        send_wishlist_discount_email(
            to_email="test@example.com",
            user_name="Test User",
            product_name="Creatine",
            old_price=100.0,
            new_price=80.0,
        )

        # sendmail was called once
        assert mock_server.sendmail.call_count == 1
        args = mock_server.sendmail.call_args
        # Second positional arg is the recipient
        assert args[0][1] == "test@example.com"

    @patch("core.discount_email.smtplib.SMTP")
    def test_subject_contains_product_name(self, mock_smtp_cls):
        """Email subject includes the product name."""
        from core.discount_email import send_wishlist_discount_email

        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__.return_value = mock_server

        send_wishlist_discount_email(
            to_email="test@example.com",
            user_name="Test User",
            product_name="Creatine",
            old_price=100.0,
            new_price=80.0,
        )

        raw_message = mock_server.sendmail.call_args[0][2]
        assert "Creatine" in raw_message

    @patch("core.discount_email.smtplib.SMTP")
    def test_email_body_contains_prices(self, mock_smtp_cls):
        """Email body includes both old and new price."""
        import base64

        from core.discount_email import send_wishlist_discount_email

        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__.return_value = mock_server

        send_wishlist_discount_email(
            to_email="test@example.com",
            user_name="Test User",
            product_name="Creatine",
            old_price=100.0,
            new_price=80.0,
        )

        raw_message = mock_server.sendmail.call_args[0][2]

        # MIME parts are base64-encoded; decode all chunks and check combined text
        decoded = ""
        for chunk in raw_message.split("\n"):
            try:
                decoded += base64.b64decode(chunk).decode("utf-8", errors="ignore")
            except Exception:
                decoded += chunk

        assert "100.00" in decoded
        assert "80.00" in decoded
