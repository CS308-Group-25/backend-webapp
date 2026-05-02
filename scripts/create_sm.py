import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from modules.auth.model import User
from modules.auth.service import pwd_context


def create_sm():
    db = SessionLocal()
    try:
        email = "sales@example.com"
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print("Sales manager user already exists.")
            return

        sm = User(
            name="Sales Manager",
            email=email,
            password_hash=pwd_context.hash("sales_password"),
            role="sales_manager",
            tax_id="0000000000",
            address="Sales Office",
        )
        db.add(sm)
        db.commit()
        print("Created sales@example.com / sales_password")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_sm()
