from decimal import Decimal

from sqlalchemy.orm import Session, joinedload

from modules.orders.model import Order, OrderItem, Payment


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_order_id(self, order_id: int) -> Order | None:
        return self.db.query(Order).filter(Order.id == order_id).first()

    def get_orders_by_user_id(self, user_id: int) -> list[Order]:
        return self.db.query(Order).filter(Order.user_id == user_id).all()

    def get_all_orders(self, status: str | None = None) -> list[Order]:
        query = self.db.query(Order).options(
            joinedload(Order.user), joinedload(Order.items)
        )
        if status:
            query = query.filter(Order.status == status)
        return query.all()

    def create_order(
        self,
        user_id: int,
        cart_id: int,
        delivery_address: str,
        status: str,
        total: Decimal,
    ) -> Order:
        order = Order(
            user_id=user_id,
            cart_id=cart_id,
            delivery_address=delivery_address,
            status=status,
            total=total,
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def create_order_item(
        self,
        order_id: int,
        product_id: int,
        quantity: int,
        price: Decimal,
    ) -> OrderItem:
        order_item = OrderItem(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            price=price,
        )
        self.db.add(order_item)
        self.db.commit()
        self.db.refresh(order_item)
        return order_item

    def create_payment(
        self,
        order_id: int,
        card_last4: str,
        card_brand: str,
        status: str,
    ) -> Payment:
        payment = Payment(
            order_id=order_id,
            card_last4=card_last4,
            card_brand=card_brand,
            status=status,
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def update_order_status(self, order_id: int, status: str) -> Order | None:
        order = self.get_by_order_id(order_id)
        if order:
            order.status = status
            self.db.commit()
            self.db.refresh(order)
        return order
