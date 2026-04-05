from fastapi import HTTPException

from core.payment import process_payment
from modules.cart.repository import CartRepository
from modules.orders.repository import OrderRepository
from modules.orders.schema import OrderItemResponse, OrderRequest, OrderResponse
from modules.products.repository import ProductRepository


class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        cart_repo: CartRepository,
        product_repo: ProductRepository,
    ):
        self.order_repo = order_repo
        self.cart_repo = cart_repo
        self.product_repo = product_repo

    def place_order(self, user_id: int, data: OrderRequest) -> OrderResponse:
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

        return OrderResponse(
            id=order.id,
            status=order.status,
            total=order.total,
            invoice_id=None,     # TODO: wire in T-136 when InvoiceService is complete
            delivery_address =order.delivery_address,
            created_at=order.created_at,
            items=[
                OrderItemResponse(
                    product_id=item.product_id,
                    name=item.product.name,
                    quantity=item.quantity,
                    price=item.price
                ) for item in order.items
            ],
        )
