import io
import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from modules.invoices.model import Invoice
from modules.invoices.repository import InvoiceRepository


class InvoiceService:
    def __init__(self, invoice_repo: InvoiceRepository):
        self.invoice_repo = invoice_repo

    def generate_invoice(self, order) -> Invoice:
        invoice_number = self._generate_invoice_number(order.id)
        pdf_bytes = self._build_pdf(order, invoice_number)
        pdf_path = self._save_pdf(invoice_number, pdf_bytes)

        return self.invoice_repo.create(
            order_id=order.id,
            invoice_number=invoice_number,
            total=order.total,
            pdf_path=pdf_path,
        )


    def _generate_invoice_number(self, order_id: int) -> str:
        year = datetime.now().year
        return f"INV-{year}-{order_id:05d}"
    
    def _build_pdf(self, order, invoice_number:str) -> bytes:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        # title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 800, f"Invoice: {invoice_number}")
        # order information
        c.setFont("Helvetica", 12)
        c.drawString(50, 770, f"Order ID: {order.id}")
        c.drawString(50, 750, f"Date: {order.created_at.strftime('%Y-%m-%d')}")
        c.drawString(50, 730, f"Customer: {order.user.name}")
        c.drawString(50, 710, f"Address: {order.delivery_address}")
        # products
        y = 680
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, "Items:")
        y -= 20
        c.setFont("Helvetica", 11)
        for item in order.items:
            line = ( f" {item.product.name} x{item.quantity}"
                    f" @ {item.price} = {item.quantity * item.price}" 
            )
            c.drawString(50, y, line)
            y -= 18
        # total
        y -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"Total: {order.total}")
        c.save()
        return buffer.getvalue()

    def _save_pdf(self, invoice_number: str, pdf_bytes: bytes) -> str:
        pdf_dir = "storage/invoices"
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = f"{pdf_dir}/{invoice_number}.pdf"
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        return pdf_path