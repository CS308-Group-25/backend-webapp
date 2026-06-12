from datetime import datetime, timezone

from fastapi import HTTPException

from core.email import send_invoice_email
from core.payment import process_payment
from modules.cart.repository import CartRepository
from modules.invoices.service import InvoiceService
from modules.orders.model import Order
from modules.orders.repository import OrderRepository
from modules.orders.schema import (
    AdminOrderResponse,
    OrderItemResponse,
    OrderRequest,
    OrderResponse,
)
from modules.payments import optional_str, payment_method_label
from modules.products.repository import ProductRepository
from modules.refunds.repository import RefundRepository


class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        cart_repo: CartRepository,
        product_repo: ProductRepository,
        invoice_service: InvoiceService | None = None,
        refund_repo: RefundRepository | None = None,
    ):
        self.order_repo = order_repo
        self.cart_repo = cart_repo
        self.product_repo = product_repo
        self.invoice_service = invoice_service
        self.refund_repo = refund_repo

    def _created_at_value(self, order: Order):
        created_at = getattr(order, "created_at", None)
        if isinstance(created_at, datetime | str):
            return created_at
        return datetime.now(timezone.utc)

    def _invoice_id(self, order: Order) -> int | None:
        invoice = getattr(order, "invoice", None)
        invoice_id = getattr(invoice, "id", None)
        return invoice_id if isinstance(invoice_id, int) else None

    def _invoice_number(self, order: Order) -> str | None:
        invoice = getattr(order, "invoice", None)
        return optional_str(getattr(invoice, "invoice_number", None))

    def _build_order_response(self, order: Order) -> OrderResponse:
        """
        Converts a SQLAlchemy Order object into an OrderResponse Pydantic schema.
        Accepts an already-fetched Order instance — does not query the database.
        Used by place_order(), get_order_by_id(), and get_user_orders() to avoid
        duplicating the response construction logic.
        """
        return OrderResponse(
            id=order.id,
            status=order.status,
            total=order.total,
            invoice_id=self._invoice_id(order),
            delivery_address=order.delivery_address,
            created_at=self._created_at_value(order),
            payment_method=payment_method_label(order),
            items=[
                OrderItemResponse(
                    id=order_item.id,
                    product_id=order_item.product_id,
                    name=order_item.product.name,
                    quantity=order_item.quantity,
                    price=order_item.price,
                    variant_name=optional_str(
                        getattr(order_item, "variant_name", None)
                    ),
                    refund_request=(
                        self.refund_repo.get_by_order_item(order_item.id)
                        if self.refund_repo
                        else None
                    ),
                )
                for order_item in order.items
            ],
        )

    def get_order_by_id(self, order_id: int, user_id: int) -> OrderResponse:
        order = self.order_repo.get_by_order_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access forbidden")
        return self._build_order_response(order)

    def get_user_orders(self, user_id: int) -> list[OrderResponse]:
        orders_list = self.order_repo.get_orders_by_user_id(user_id)
        return [self._build_order_response(order) for order in orders_list]

    def place_order(self, user_id: int, data: OrderRequest) -> OrderResponse:
        if self.invoice_service is None:
            raise RuntimeError("invoice_service required for place_order")

        cart = self.cart_repo.get(user_id)
        if not cart or not cart.items:
            raise HTTPException(
                status_code=400, detail="Cart is empty, cannot place order."
            )

        # Stock checks and total price calculation
        total = 0
        for item in cart.items:
            product = self.product_repo.get_by_id(item.product_id)
            if not product:
                raise HTTPException(
                    status_code=404, detail=f"Product {item.product_id} not found"
                )

            if product.stock == 0:
                raise HTTPException(
                    status_code=400, detail=f"Product {product.name} is out of stock"
                )

            elif product.stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for {product.name} request",
                )

            if product.price is None:
                raise HTTPException(
                    status_code=400,
                    detail=(
                    f"Product '{product.name}' has no price set yet. A Sales "
                    "Manager must set the price before it can be purchased."
                ),
                )

            total += item.quantity * product.price

        # Atomic block: stock re-validation under lock, payment, order creation,
        # stock decrement, and payment recording are committed together — rollback
        # on any failure ensures no partial state. The card is only charged once
        # stock is reserved under the row locks, so a checkout that loses the race
        # for the last item is rejected before any payment is taken.
        try:
            # Lock each product row and re-validate stock under the lock.
            locked_products: dict[int, object] = {}
            for item in cart.items:
                product = self.product_repo.get_by_id_for_update(item.product_id)

                if not product:
                    raise HTTPException(
                        status_code=404, detail=f"Product {item.product_id} not found"
                    )
                if product.stock < item.quantity:
                    raise HTTPException(
                        status_code=409,
                        detail=f"Insufficient stock for {product.name}: "
                        f"requested {item.quantity}, available {product.stock}",
                    )

                locked_products[item.product_id] = product

            # Charge only after every row is locked and stock confirmed. The locks
            # are held until the commit/rollback below, so the reserved units
            # cannot be taken by a concurrent checkout between this charge and the
            # commit — no charge can succeed without a guaranteed reservation.
            payment_success = process_payment(
                card_number=data.card_number,
                card_last4=data.card_last4,
                card_brand=data.card_brand,
                amount=total,
            )
            if not payment_success:
                raise HTTPException(status_code=400, detail="Payment failed")

            order = self.order_repo.create_order(
                user_id=user_id,
                cart_id=cart.id,
                delivery_address=data.delivery_address,
                status="confirmed",
                total=total,
            )

            for item in cart.items:
                product = locked_products[item.product_id]
                self.order_repo.create_order_item(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=item.quantity,
                    price=product.price or 0,
                    variant_name=item.variant_name,
                )
                self.product_repo.update_stock(product.id, item.quantity)
            _ = self.order_repo.create_payment(
                order_id=order.id,
                card_last4=data.card_last4,
                card_brand=data.card_brand,
                status="success",
            )

            self.order_repo.db.commit()  # all in one commit - assure atomicity
            self.order_repo.db.refresh(order)

        except HTTPException:
            self.order_repo.db.rollback()
            raise

        except Exception:
            self.order_repo.db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Order could not be completed. Please try again.",
            )

        for item in cart.items:
            self.cart_repo.remove_item(item.id)

        invoice = self.invoice_service.generate_invoice(order)
        send_invoice_email(
            to_email=order.user.email,
            invoice_number=invoice.invoice_number,
            pdf_path=invoice.pdf_path,
        )

        return self._build_order_response(order)

    def update_order_status(self, order_id: int, new_status: str) -> OrderResponse:
        order = self.order_repo.get_by_order_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.status == "cancelled":
            raise HTTPException(status_code=400, detail=
                                "Cannot update a cancelled order")

        # valid_transitions = {
        #     "confirmed": ["processing"],
        #     "processing": ["in_transit"],
        #     "in_transit": ["delivered"],
        # }

        # current_status = order.status

        # # If trying to transition to the same status, we can just return (idempotent)
        # if current_status == new_status:
        #     return self._build_order_response(order)

        # allowed = valid_transitions.get(current_status, [])
        # if new_status not in allowed:
        #     raise HTTPException(
        #         status_code=400,
        #         detail=(
        #             f"Invalid status transition from {current_status} to {new_status}"
        #         ),
        #     )

        updated_order = self.order_repo.update_order_status(order_id, new_status)
        return self._build_order_response(updated_order)

    def get_admin_orders(self, status: str | None = None) -> list[AdminOrderResponse]:
        orders = self.order_repo.get_all_orders(status)
        results = []
        for order in orders:
            results.append(
                AdminOrderResponse(
                    order_id=order.id,
                    customer_id=order.user_id,
                    total=order.total,
                    invoice_id=self._invoice_id(order),
                    invoice_number=self._invoice_number(order),
                    items=[
                        OrderItemResponse(
                            id=item.id,
                            product_id=item.product_id,
                            name=item.product.name,
                            quantity=item.quantity,
                            price=item.price,
                            variant_name=optional_str(
                                getattr(item, "variant_name", None)
                            ),
                        )
                        for item in order.items
                    ],
                    delivery_address=order.delivery_address,
                    status=order.status,
                    completed=(order.status == "delivered"),
                    customer_name=order.user.name,
                    customer_email=order.user.email,
                    created_at=self._created_at_value(order),
                    payment_method=payment_method_label(order),
                )
            )
        return results

    def cancel_order(self, order_id: int, user_id: int) -> OrderResponse:
        order = self.order_repo.get_by_order_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found.")
        if order.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access forbidden.")

        CANCALLABLE_STATUSES = {"pending", "confirmed", "processing"}
        if order.status not in CANCALLABLE_STATUSES:
            raise HTTPException(
                status_code=400,
                detail="Order cannot be cancelled once it is being procesed.",
            )

        updated_order = self.order_repo.update_order_status(order_id, "cancelled")

        # Restore stock for each item in the cancelled order
        for item in order.items:
            self.product_repo.increment_stock(item.product_id, item.quantity)

        self.order_repo.db.commit()

        return self._build_order_response(updated_order)
