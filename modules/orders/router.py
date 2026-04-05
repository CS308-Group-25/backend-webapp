from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from modules.auth.model import User
from modules.cart.repository import CartRepository
from modules.orders.repository import OrderRepository
from modules.orders.schema import OrderRequest, OrderResponse
from modules.orders.service import OrderService
from modules.products.repository import ProductRepository

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])

@router.post("/", response_model=OrderResponse, status_code=201)
def place_order(
    data: OrderRequest, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    order_repo = OrderRepository(db)
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    service = OrderService(order_repo, cart_repo, product_repo)
    return service.place_order(current_user.id, data)
