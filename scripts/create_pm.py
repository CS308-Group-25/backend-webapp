import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from modules.auth.model import User
from modules.auth.service import pwd_context


def create_pm():
    db = SessionLocal()
    try:
        email = os.getenv("PM_EMAIL", "pm@example.com")
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print("PM user already exists.")
            return

        pm = User(
            name="Product Manager",
            email=email,
            password_hash=pwd_context.hash(os.getenv("PM_PASSWORD", "pm_password")),
            role="product_manager",
            tax_id=os.getenv("PM_TAX_ID", "1234567890"),
            address=os.getenv("PM_ADDRESS", "PM Office"),
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
