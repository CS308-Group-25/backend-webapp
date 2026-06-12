from sqlalchemy.orm import Session

from modules.addresses.model import Address


class AddressRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user(self, user_id: int) -> list[Address]:
        return (
            self.db.query(Address)
            .filter(Address.user_id == user_id)
            .order_by(Address.created_at.desc())
            .all()
        )

    def create(self, user_id: int, data) -> Address:
        addr = Address(
            user_id=user_id,
            title=data.title,
            first_name=data.first_name,
            last_name=data.last_name,
            address=data.address,
            apartment=data.apartment or None,
            city=data.city,
            district=data.district,
            phone=data.phone,
        )
        self.db.add(addr)
        self.db.commit()
        self.db.refresh(addr)
        return addr

    def delete(self, address_id: int, user_id: int) -> bool:
        addr = (
            self.db.query(Address)
            .filter(Address.id == address_id, Address.user_id == user_id)
            .first()
        )
        if not addr:
            return False
        self.db.delete(addr)
        self.db.commit()
        return True
