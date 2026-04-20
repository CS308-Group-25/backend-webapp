import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from core.database import SessionLocal
from modules.auth.model import User
from modules.auth.service import pwd_context


def create_pm():
    db = SessionLocal()
    try:
        email = "pm@example.com"
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print("PM user already exists.")
            return

        pm = User(
            name="Product Manager",
            email=email,
            password_hash=pwd_context.hash("pm_password"),
            role="product_manager",
            tax_id="1234567890", # Added dummy tax_id to satisfy DB constraint
            address="PM Office" # Added dummy address
        )
        db.add(pm)
        db.commit()
        print(f"Successfully created PM user: {email} / pm_password")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_pm()
