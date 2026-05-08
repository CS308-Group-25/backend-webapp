import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from modules.auth.model import User
from modules.auth.service import pwd_context


def create_sm():
    email = os.getenv("SM_EMAIL")
    password = os.getenv("SM_PASSWORD")
    tax_id = os.getenv("SM_TAX_ID")
    address = os.getenv("SM_ADDRESS")

    missing = [k for k, v in {"SM_EMAIL": email, "SM_PASSWORD": password, "SM_TAX_ID": tax_id, "SM_ADDRESS": address}.items() if not v]
    if missing:
        print(f"Error: missing required environment variables: {', '.join(missing)}")
        sys.exit(1)

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print("Sales manager user already exists.")
            return

        sm = User(
            name="Sales Manager",
            email=email,
            password_hash=pwd_context.hash(password),
            role="sales_manager",
            tax_id=tax_id,
            address=address,
        )
        db.add(sm)
        db.commit()
        print(f"Successfully created SM user: {email}")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_sm()
