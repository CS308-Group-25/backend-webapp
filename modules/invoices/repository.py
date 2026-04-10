from sqlalchemy.orm import Session

from modules.invoices.model import Invoice


class InvoiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
            self,
            order_id: int,
            invoice_number: str,
            total,
            pdf_path: str | None = None,
    ) -> Invoice:
        invoice = Invoice(
            order_id=order_id,
            invoice_number=invoice_number,
            total=total,
            pdf_path=pdf_path,
        )
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice
    
    def get_by_order_id(self, order_id: int) -> Invoice | None:
        return self.db.query(Invoice).filter(Invoice.order_id == order_id).first()