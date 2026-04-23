import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_wishlist_discount_email(
    to_email: str,
    user_name: str,
    product_name: str,
    old_price: float,
    new_price: float,
) -> None:
    """Send a discount notification email to a user who wishlisted the product.

    Args:
        to_email: Recipient's email address.
        user_name: Recipient's display name.
        product_name: Name of the discounted product.
        old_price: The product's previous price.
        new_price: The product's new discounted price.
    """
    msg = _build_discount_message(
        to_email, user_name, product_name, old_price, new_price
    )
    _send_via_smtp(to_email, msg)


def _build_discount_message(
    to_email: str,
    user_name: str,
    product_name: str,
    old_price: float,
    new_price: float,
) -> MIMEMultipart:
    """Build the MIME email message for the discount notification."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Price drop on {product_name} in your wishlist!"
    msg["From"] = os.getenv("EMAIL_FROM", "no-reply@supplements.com")
    msg["To"] = to_email

    discount_pct = round((1 - new_price / old_price) * 100)

    plain = (
        f"Hi {user_name},\n\n"
        f"Good news! A product on your wishlist just got a price drop.\n\n"
        f"Product: {product_name}\n"
        f"Old price: {old_price:.2f} TL\n"
        f"New price: {new_price:.2f} TL  ({discount_pct}% off)\n\n"
        f"Head over to the store to grab it before it sells out!\n\n"
        f"— Supplements Store"
    )

    html = f"""\
<html>
  <body style="font-family:Arial,sans-serif;color:#333;max-width:600px;margin:auto;">
    <h2 style="color:#e05c00;">&#127881; Price drop on your wishlist item!</h2>
    <p>Hi <strong>{user_name}</strong>,</p>
    <p>
      A product you wishlisted is now on sale:
    </p>
    <table style="border-collapse:collapse;width:100%;margin:16px 0;">
      <tr>
        <td style="padding:8px;border:1px solid #ddd;">Product</td>
        <td style="padding:8px;border:1px solid #ddd;">
          <strong>{product_name}</strong>
        </td>
      </tr>
      <tr>
        <td style="padding:8px;border:1px solid #ddd;">Old price</td>
        <td style="padding:8px;border:1px solid #ddd;"
            style="text-decoration:line-through;color:#999;">
          {old_price:.2f} TL
        </td>
      </tr>
      <tr>
        <td style="padding:8px;border:1px solid #ddd;">New price</td>
        <td style="padding:8px;border:1px solid #ddd;
                   color:#e05c00;font-weight:bold;">
          {new_price:.2f} TL &nbsp;
          <span style="font-size:12px;">({discount_pct}% off)</span>
        </td>
      </tr>
    </table>
    <p>Don't miss out — head to the store and grab it!</p>
    <p style="color:#888;font-size:12px;">— Supplements Store</p>
  </body>
</html>"""

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html, "html"))
    return msg


def _send_via_smtp(to_email: str, msg: MIMEMultipart) -> None:
    """Send a pre-built MIME message via SMTP."""
    host = os.getenv("MAIL_SERVER", "localhost")
    port = int(os.getenv("MAIL_PORT", "1025"))
    username = os.getenv("MAIL_USERNAME", "")
    password = os.getenv("MAIL_PASSWORD", "")

    with smtplib.SMTP(host, port) as server:
        if username and password:
            server.starttls()
            server.login(username, password)
        server.sendmail(msg["From"], to_email, msg.as_string())
