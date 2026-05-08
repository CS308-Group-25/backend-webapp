import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from modules.auth.model import User
from modules.auth.service import pwd_context


def create_pm():
    email = os.getenv("PM_EMAIL")
    password = os.getenv("PM_PASSWORD")
    tax_id = os.getenv("PM_TAX_ID")
    address = os.getenv("PM_ADDRESS")

    missing = [k for k, v in {"PM_EMAIL": email, "PM_PASSWORD": password, "PM_TAX_ID": tax_id, "PM_ADDRESS": address}.items() if not v]
    if missing:
        print(f"Error: missing required environment variables: {', '.join(missing)}")
        sys.exit(1)

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print("PM user already exists.")
            return

        pm = User(
            name="Product Manager",
            email=email,
            password_hash=pwd_context.hash(password),
            role="product_manager",
            tax_id=tax_id,
            address=address,
        )
        db.add(pm)
        db.commit()
        print(f"Successfully created PM user: {email}")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_pm()
