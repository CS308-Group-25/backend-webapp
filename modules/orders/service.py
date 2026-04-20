from fastapi import HTTPException

from core.email import send_invoice_email
from core.payment import process_payment
from modules.cart.repository import CartRepository
from modules.invoices.service import InvoiceService
from modules.orders.model import Order
from modules.orders.repository import OrderRepository
from modules.orders.schema import OrderItemResponse, OrderRequest, OrderResponse
from modules.products.repository import ProductRepository


class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        cart_repo: CartRepository,
        product_repo: ProductRepository,
        invoice_service: InvoiceService | None = None,
    ):
        self.order_repo = order_repo
        self.cart_repo = cart_repo
        self.product_repo = product_repo
        self.invoice_service = invoice_service

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
            invoice_id=order.invoice.id if order.invoice else None,
            delivery_address=order.delivery_address,
            created_at=order.created_at,
            items=[
                OrderItemResponse(
                    product_id=order_item.product_id,
                    name=order_item.product.name,
                    quantity=order_item.quantity,
                    price=order_item.price,
                ) for order_item in order.items
            ]
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
            raise RuntimeError("invoice_service requried for place_order")
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

            total += item.quantity * product.price

        # Try to process payment
        payment_success = process_payment(
            card_number=data.card_number,
            card_last4=data.card_last4,
            card_brand=data.card_brand,
            amount=total,
        )
        if not payment_success:
            raise HTTPException(status_code=400, detail="Payment failed")

        # Process order
        order = self.order_repo.create_order(
            user_id=user_id,
            cart_id=cart.id,
            delivery_address=data.delivery_address,
            status="confirmed",
            total=total,
        )

        # Decrease stock and write to product repo
        for item in cart.items:
            product = self.product_repo.get_by_id(item.product_id)
            self.order_repo.create_order_item(
                order_id=order.id,
                product_id=product.id,
                quantity=item.quantity,
                price=product.price,
            )
            self.product_repo.update_stock(product.id, item.quantity)

        # Create payment but since payment variable will not be used it is not written
        # TODO: Will update variable name once Invoice tasks are done
        _ = self.order_repo.create_payment(
            order_id=order.id,
            card_last4=data.card_last4,
            card_brand=data.card_brand,
            status="success",
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

        valid_transitions = {
            "confirmed": ["processing"],
            "processing": ["in_transit"],
            "in_transit": ["delivered"],
        }

        current_status = order.status
        
        # If trying to transition to the same status, we can just return (idempotent)
        if current_status == new_status:
            return self._build_order_response(order)

        allowed = valid_transitions.get(current_status, [])
        if new_status not in allowed:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid status transition from "
                    f"{current_status} to {new_status}"
                ),
            )


        updated_order = self.order_repo.update_order_status(order_id, new_status)
        return self._build_order_response(updated_order)


