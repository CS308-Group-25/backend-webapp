import logging
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


def send_invoice_email(to_email: str, invoice_number: str, pdf_path: str) -> None:
    """Send invoice email. Fails silently if SMTP is not configured."""
    try:
        _send_via_smtp(to_email, invoice_number, pdf_path)
        logger.info(f"Invoice email sent to {to_email} for invoice {invoice_number}")
    except Exception as exc:
        # Email delivery is non-critical — log a warning and continue.
        # The order has already been placed successfully.
        logger.warning(
            f"Failed to send invoice email to {to_email} "
            f"(invoice {invoice_number}): {exc}"
        )


def _build_message(to_email: str, invoice_number: str, pdf_path: str) -> MIMEMultipart:
    msg = MIMEMultipart()
    msg["Subject"] = f"Your Invoice {invoice_number}"
    msg["From"] = os.getenv("EMAIL_FROM", "no-reply@supplements.com")
    msg["To"] = to_email
    msg.attach(
        MIMEText(f"Please find your invoice {invoice_number} attached.", "plain")
    )

    with open(pdf_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition", f"attachment; filename={invoice_number}.pdf"
        )
        msg.attach(part)

    return msg


def _send_via_smtp(to_email: str, invoice_number: str, pdf_path: str) -> None:
    host = os.getenv("MAIL_SERVER", "")
    if not host:
        raise ValueError("MAIL_SERVER environment variable is not set")

    port = int(os.getenv("MAIL_PORT", "587"))
    username = os.getenv("MAIL_USERNAME", "")
    password = os.getenv("MAIL_PASSWORD", "")

    msg = _build_message(to_email, invoice_number, pdf_path)

    with smtplib.SMTP(host, port) as server:
        if username and password:
            server.starttls()
            server.login(username, password)
        server.sendmail(msg["From"], to_email, msg.as_string())

