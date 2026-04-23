from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user, require_product_manager
from modules.auth.model import User
from modules.cart.repository import CartRepository
from modules.invoices.repository import InvoiceRepository
from modules.invoices.service import InvoiceService
from modules.orders.repository import OrderRepository
from modules.orders.schema import (
    AdminOrderResponse,
    OrderItemResponse,
    OrderRequest,
    OrderResponse,
    StatusUpdateRequest,
)
from modules.orders.service import OrderService
from modules.products.repository import ProductRepository

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])
admin_router = APIRouter(prefix="/api/v1/admin/orders", tags=["admin-orders"])


@router.post("", response_model=OrderResponse, status_code=201)
def place_order(
    data: OrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order_repo = OrderRepository(db)
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    invoice_repo = InvoiceRepository(db)
    invoice_service = InvoiceService(invoice_repo)
    service = OrderService(order_repo, cart_repo, product_repo, invoice_service)
    return service.place_order(current_user.id, data)


@router.get("", response_model=list[OrderResponse], status_code=200)
def get_user_orders(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    order_repo = OrderRepository(db)
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    service = OrderService(order_repo, cart_repo, product_repo)
    return service.get_user_orders(current_user.id)


@router.get("/{order_id}", response_model=OrderResponse, status_code=200)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order_repo = OrderRepository(db)
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    service = OrderService(order_repo, cart_repo, product_repo)
    return service.get_order_by_id(order_id, current_user.id)


@admin_router.get("", response_model=list[AdminOrderResponse], status_code=200)
def get_admin_orders(
    status: str | None = None,
    current_user: User = Depends(require_product_manager),
    db: Session = Depends(get_db),
):
    order_repo = OrderRepository(db)
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    service = OrderService(order_repo, cart_repo, product_repo)
    return service.get_admin_orders(status)


@admin_router.patch("/{order_id}", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    data: StatusUpdateRequest,
    db: Session = Depends(get_db),
):
    # TODO: Add require_product_manager before production
    order_repo = OrderRepository(db)
    updated_order = order_repo.update_order_status(order_id, data.status)
    if not updated_order:
        raise HTTPException(status_code=404, detail="Order not found")

    return OrderResponse(
        id=updated_order.id,
        status=updated_order.status,
        total=updated_order.total,
        invoice_id=updated_order.invoice.id if updated_order.invoice else None,
        delivery_address=updated_order.delivery_address,
        created_at=updated_order.created_at,
        items=[
            OrderItemResponse(
                product_id=item.product_id,
                name=item.product.name,
                quantity=item.quantity,
                price=item.price,
            )
            for item in updated_order.items
        ],
    )


@router.patch("/{order_id}", response_model=OrderResponse, status_code=200)
def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order_repo = OrderRepository(db)
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    service = OrderService(order_repo, cart_repo, product_repo)
    return service.cancel_order(order_id=order_id, user_id=current_user.id)
