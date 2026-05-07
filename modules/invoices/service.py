import io
import os
import pathlib
import sys
import tempfile
from datetime import date, datetime
from decimal import Decimal

import reportlab
from xhtml2pdf import pisa

from modules.invoices.model import Invoice
from modules.invoices.repository import InvoiceRepository
from modules.invoices.schema import AdminInvoiceListItem

_MONTHS_TR = [
    "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
    "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık",
]


def _patch_pisa_windows() -> None:
    """Fix xhtml2pdf NamedTemporaryFile locking bug on Windows.

    Without delete=False, Windows locks the temp file while it's open,
    preventing ReportLab from opening it by name to load the font.
    """
    if sys.platform != "win32":
        return
    import xhtml2pdf.files as _pf
    if getattr(_pf.BaseFile, "_win32_patched", False):
        return

    def _patched_get_named_tmp_file(self):
        data = self.get_data()
        tmp = tempfile.NamedTemporaryFile(suffix=self.suffix, delete=False)
        if data:
            tmp.write(data)
            tmp.flush()
        tmp.close()
        _pf.files_tmp.append(tmp)
        if self.path is None:
            self.path = tmp.name
        return tmp

    _pf.BaseFile.get_named_tmp_file = _patched_get_named_tmp_file
    _pf.BaseFile._win32_patched = True


class InvoiceService:
    def __init__(self, invoice_repo: InvoiceRepository):
        self.invoice_repo = invoice_repo

    def get_by_order_id(self, order_id: int) -> Invoice | None:
        return self.invoice_repo.get_by_order_id(order_id)

    def get_by_id(self, invoice_id: int) -> Invoice | None:
        return self.invoice_repo.get_by_id(invoice_id)

    def list_admin(
        self,
        from_date: date | None,
        to_date: date | None,
        page: int,
        page_size: int,
    ) -> tuple[list[AdminInvoiceListItem], int]:
        invoices, total = self.invoice_repo.list_admin(
            from_date,
            to_date,
            page,
            page_size
        )
        items = [
            AdminInvoiceListItem(
                id=inv.id,
                invoice_number=inv.invoice_number,
                customer_name=inv.order.user.name,
                total=inv.total,
                created_at=inv.created_at,
            )
            for inv in invoices
        ]
        return items, total

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

    def _build_pdf(self, order, invoice_number: str) -> bytes:
        subtotal = sum(item.quantity * item.price for item in order.items)
        tax_amount = round(Decimal(str(subtotal)) * Decimal("0.01"), 2)
        total_with_tax = subtotal + tax_amount

        _patch_pisa_windows()

        font_dir = pathlib.Path(reportlab.__file__).parent / "fonts"

        def _link_callback(uri, _rel):
            if uri in ("Vera.ttf", "VeraBd.ttf"):
                return str(font_dir / uri)
            return uri

        html = self._render_html(
            order, invoice_number, subtotal, tax_amount, total_with_tax
        )
        buffer = io.BytesIO()
        result = pisa.CreatePDF(
            html, dest=buffer, link_callback=_link_callback, encoding="utf-8"
        )
        if result.err:
            raise RuntimeError(f"PDF generation error: {result.err}")
        return buffer.getvalue()

    def _fmt(self, amount) -> str:
        s = f"{float(amount):,.2f}"
        return s.replace(",", "X").replace(".", ",").replace("X", ".")

    def _fmt_date(self, dt) -> str:
        return f"{dt.day:02d} {_MONTHS_TR[dt.month - 1]} {dt.year}"

    def _split_address(self, delivery_address: str) -> tuple[str, str]:
        parts = [p.strip() for p in delivery_address.split(",") if p.strip()]
        for i, part in enumerate(parts):
            digits = "".join(c for c in part if c.isdigit())
            if 10 <= len(digits) <= 12:
                d = digits[-10:]
                phone = f"+90 {d[:3]} {d[3:6]} {d[6:8]} {d[8:]}"
                address = ", ".join(p for j, p in enumerate(parts) if j != i)
                return phone, address
        return "", delivery_address

    def _render_html(
        self, order, invoice_number, subtotal, tax_amount, total_with_tax
    ) -> str:
        phone, address = self._split_address(order.delivery_address)
        date_str = self._fmt_date(order.created_at)
        payment_method = (
            f"Kredi Kartı (*{order.payment.card_last4})"
            if order.payment
            else "Kredi Kartı"
        )

        items_rows = ""
        for item in order.items:
            total_price = item.quantity * item.price
            items_rows += (
                f"<tr>"
                f"<td style='font-family:VFB;font-size:11pt;"
                f"color:#0f172a;padding:10px 0;"
                f"border-bottom:1px solid #f8fafc;'>{item.product.name}</td>"
                f"<td style='text-align:center;color:#5D5CFF;"
                f"font-family:VFB;padding:10px 0;"
                f"border-bottom:1px solid #f8fafc;'>{item.quantity}</td>"
                f"<td style='text-align:right;color:#64748b;"
                f"padding:10px 0;border-bottom:1px solid #f8fafc;'>"
                f"{self._fmt(item.price)} TL</td>"
                f"<td style='text-align:right;font-family:VFB;"
                f"color:#0f172a;padding:10px 0;"
                f"border-bottom:1px solid #f8fafc;'>"
                f"{self._fmt(total_price)} TL</td>"
                f"</tr>"
            )

        phone_row = (
            f"<p style='font-size:10pt;color:#475569;margin-top:3px;'>{phone}</p>"
            if phone
            else ""
        )

        return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"/>
<style>
@font-face {{ font-family: VF;  src: url("Vera.ttf"); }}
@font-face {{ font-family: VFB; src: url("VeraBd.ttf"); }}
* {{ margin:0; padding:0; }}
body {{ font-family:VF; font-size:10pt; color:#1e293b; }}
</style>
</head><body>

<table width="100%" cellpadding="0" cellspacing="0"
  style="background-color:#5D5CFF;">
<tr>
  <td style="vertical-align:top;padding:25px 0 12px 40px;">
    <p style="font-family:VFB;font-size:7pt;color:#c7d2fe;">SUPPLEMENTS</p>
    <p style="font-family:VFB;font-size:20pt;color:white;margin-top:4px;">FATURA</p>
  </td>
  <td style="vertical-align:top;text-align:right;padding:25px 40px 12px 0;">
    <p style="font-family:VFB;font-size:15pt;color:white;">{invoice_number}</p>
    <p style="font-size:9pt;color:#c7d2fe;">Sipariş #{order.id}</p>
  </td>
</tr>
</table>

<table width="100%" cellpadding="0" cellspacing="0"
  style="background-color:#5D5CFF;">
<tr>
  <td width="25%" style="vertical-align:top;padding:0 8px 25px 40px;">
    <p style="font-family:VFB;font-size:7pt;color:#c7d2fe;">TARİH</p>
    <p style="font-family:VFB;font-size:10pt;color:white;margin-top:4px;">{date_str}</p>
  </td>
  <td width="25%" style="vertical-align:top;padding:0 8px 25px 0;">
    <p style="font-family:VFB;font-size:7pt;color:#c7d2fe;">ÖDEME YÖNTEMİ</p>
    <p style="font-family:VFB;font-size:10pt;color:white;
margin-top:4px;">{payment_method}</p>
  </td>
  <td width="25%" style="vertical-align:top;padding:0 8px 25px 0;">
    <p style="font-family:VFB;font-size:7pt;color:#c7d2fe;">ÖDEME DURUMU</p>
    <p style="font-family:VFB;font-size:10pt;color:white;margin-top:4px;">Ödendi</p>
  </td>
  <td width="25%" style="vertical-align:top;padding:0 40px 25px 0;">
    <p style="font-family:VFB;font-size:7pt;color:#c7d2fe;">SİPARİŞ TARİHİ</p>
    <p style="font-family:VFB;font-size:10pt;color:white;margin-top:4px;">{date_str}</p>
  </td>
</tr>
</table>

<div style="padding:20px 40px;border-bottom:1px solid #f1f5f9;">
  <p style="font-family:VFB;font-size:7pt;color:#94a3b8;
margin-bottom:10px;">FATURA ADRESİ</p>
  <p style="font-family:VFB;font-size:12pt;color:#0f172a;">{order.user.name}</p>
  {phone_row}
  <p style="font-size:10pt;color:#475569;margin-top:3px;">{address}</p>
  <p style="font-size:10pt;color:#475569;">Türkiye</p>
</div>

<div style="padding:20px 40px;">
  <p style="font-family:VFB;font-size:7pt;color:#94a3b8;
margin-bottom:10px;">ÜRÜNLER</p>
  <table width="100%" cellpadding="0" cellspacing="0">
    <thead>
      <tr style="border-bottom:2px solid #f1f5f9;">
        <th style="font-family:VFB;font-size:7pt;color:#94a3b8;
text-align:left;padding-bottom:8px;">ÜRÜN</th>
        <th style="font-family:VFB;font-size:7pt;color:#94a3b8;
text-align:center;padding-bottom:8px;width:55px;">ADET</th>
        <th style="font-family:VFB;font-size:7pt;color:#94a3b8;
text-align:right;padding-bottom:8px;width:110px;">BİRİM FİYAT</th>
        <th style="font-family:VFB;font-size:7pt;color:#94a3b8;
text-align:right;padding-bottom:8px;width:110px;">TUTAR</th>
      </tr>
    </thead>
    <tbody>{items_rows}</tbody>
  </table>
</div>

<div style="padding:0 40px 25px 40px;">
  <table style="float:right;min-width:220px;" cellpadding="4" cellspacing="0">
    <tr>
      <td style="font-size:10pt;color:#64748b;">Ara Toplam</td>
      <td style="font-family:VFB;text-align:right;
color:#1e293b;">{self._fmt(subtotal)} TL</td>
    </tr>
    <tr>
      <td style="font-size:10pt;color:#64748b;">KDV (%1)</td>
      <td style="font-family:VFB;text-align:right;
color:#1e293b;">{self._fmt(tax_amount)} TL</td>
    </tr>
    <tr><td colspan="2" style="border-top:1px solid #e2e8f0;padding-top:6px;"></td></tr>
    <tr>
      <td style="font-family:VFB;font-size:12pt;color:#0f172a;">Genel Toplam</td>
      <td style="font-family:VFB;font-size:12pt;
text-align:right;color:#5D5CFF;">{self._fmt(total_with_tax)} TL</td>
    </tr>
  </table>
</div>

<table width="100%" cellpadding="0" cellspacing="0"
  style="background-color:#f8fafc;padding:15px 40px;
border-top:1px solid #f1f5f9;margin-top:10px;">
<tr>
  <td style="font-size:8pt;color:#94a3b8;text-align:center;">
    Bu fatura Supplements tarafından elektronik olarak düzenlenmiştir.
    Herhangi bir sorunuz için lütfen supplements@cs308.com adresiyle iletişime geçin.
  </td>
</tr>
</table>

</body></html>"""

    def _save_pdf(self, invoice_number: str, pdf_bytes: bytes) -> str:
        pdf_dir = "storage/invoices"
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = f"{pdf_dir}/{invoice_number}.pdf"
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        return pdf_path
