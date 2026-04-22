from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user, require_product_manager
from modules.auth.model import User
from modules.cart.repository import CartRepository
from modules.invoices.repository import InvoiceRepository
from modules.invoices.service import InvoiceService
from modules.orders.repository import OrderRepository
from modules.orders.schema import AdminOrderResponse, OrderRequest, OrderResponse
from modules.orders.service import OrderService
from modules.products.repository import ProductRepository

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])
admin_router = APIRouter(prefix="/api/v1/admin/orders", tags=["admin-orders"])

@router.post("", response_model=OrderResponse, status_code=201)
def place_order(
    data: OrderRequest, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
):
    order_repo = OrderRepository(db)
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    service = OrderService(order_repo, cart_repo, product_repo)
    return service.get_admin_orders(status)

