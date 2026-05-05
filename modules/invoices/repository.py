from datetime import date

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func

from modules.invoices.model import Invoice
from modules.orders.model import Order


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

    def get_by_id(self, invoice_id: int) -> Invoice | None:
        return self.db.query(Invoice).filter(Invoice.id == invoice_id).first()

    def list_admin(
        self,
        from_date: date | None,
        to_date: date | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Invoice], int]:
        query = self.db.query(Invoice).options(
            joinedload(Invoice.order).joinedload(Order.user)
        )
        if from_date:
            query = query.filter(func.date(Invoice.created_at) >= from_date)
        if to_date:
            query = query.filter(func.date(Invoice.created_at) <= to_date)
        total = query.count()
        items = (
            query.order_by(Invoice.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total
