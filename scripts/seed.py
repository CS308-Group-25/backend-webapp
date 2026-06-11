# isort: skip_file

import json
import os
import random
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import core.models  # noqa: F401 — registers all models with SQLAlchemy metadata
from core.database import SessionLocal
from modules.auth.model import User
from modules.auth.service import pwd_context
from modules.categories.model import Category
from modules.invoices.model import Invoice
from modules.orders.model import Order, OrderItem, Payment
from modules.products.model import Product
from modules.reviews.model import Review
from modules.wishlist.model import WishlistItem


random.seed(42)


# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------


# Seed data is stored outside the scripts folder to keep scripts clean.
# Example:
# backend-webapp/seed_data/supplement_store_110_products.json
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

DATA_FILE = PROJECT_ROOT / "seed_data" / "supplement_store_demo_real_3_products.json"


# Only these 3 images are currently available.
# These files must be located under public/products on the frontend.
IMAGES_POOL = [
    "/products/bcaa.png",
    "/products/creatine.png",
    "/products/protein-bar.png",
]

DEMO_CUSTOMER = {
    "name": "Demo Musteri",
    "email": "customer@demo.com",
    "password": "demo123",
    "address": "Levent, Istanbul",
    "tax_id": "9999999999",
}

DEMO_REVIEW_COMMENTS = [
    "Urun cok kullanisli, teslimattan sonra memnun kaldim.",
    "Aromasi guzel ve kullanimi rahat.",
    "Paketleme iyiydi, urun beklentimi karsiladi.",
    "Antrenman sonrasi toparlanmada iyi hissettirdi.",
    "Fiyat performans olarak basarili buldum.",
    "Tekrar almayi dusunurum.",
    "Kargo hizliydi, urun sorunsuz geldi.",
    "Icerik bilgileri net ve kullanimi kolay.",
    "Tadi bekledigimden daha iyi cikti.",
    "Demo icin populer urun yorumudur.",
]

DEMO_REVIEW_USERS = [
    ("Mehmet Er", "demo.review.01@example.com"),
    ("Ayse Demir", "demo.review.02@example.com"),
    ("Deniz Kaya", "demo.review.03@example.com"),
    ("Ece Yilmaz", "demo.review.04@example.com"),
    ("Can Arslan", "demo.review.05@example.com"),
    ("Elif Sahin", "demo.review.06@example.com"),
    ("Burak Aydin", "demo.review.07@example.com"),
    ("Zeynep Koc", "demo.review.08@example.com"),
    ("Mert Celik", "demo.review.09@example.com"),
    ("Selin Aksoy", "demo.review.10@example.com"),
]


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


def get_value(data, *keys, default=None):
    """
    Performs a safe read in case the JSON contains fields in camelCase or snake_case.
    Example:
    originalPrice / original_price
    stockStatus / stock_status
    reviewCount / review_count
    """
    for key in keys:
        if key in data:
            return data[key]

    return default


def load_seed_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Seed JSON file not found: {DATA_FILE}")

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if "categories" not in data:
        raise ValueError("'categories' field missing in JSON.")

    if "products" not in data:
        raise ValueError("'products' field missing in JSON.")

    return data


def clean_old_data(db):
    print("Cleaning old data...")

    # Delete in FK-safe order. Savepoints let individual statements fail silently
    # (e.g. table missing on first run) without aborting the whole transaction.
    ordered_deletes = [
        "DELETE FROM refund_requests",
        "DELETE FROM invoices",
        "DELETE FROM payments",
        "DELETE FROM cart_items",
        "DELETE FROM order_items",
        "DELETE FROM wishlist_items",
        "DELETE FROM reviews",
        "DELETE FROM discounts",
        "DELETE FROM orders",
        "DELETE FROM carts",
        "DELETE FROM products",
        "DELETE FROM categories",
    ]

    for sql in ordered_deletes:
        db.execute(text("SAVEPOINT clean_sp"))
        try:
            db.execute(text(sql))
            db.execute(text("RELEASE SAVEPOINT clean_sp"))
        except Exception:
            db.execute(text("ROLLBACK TO SAVEPOINT clean_sp"))

    # User deletion runs after all FK references are cleared.
    db.execute(text("DELETE FROM users WHERE email LIKE :p"), {"p": "%@example.com"})
    db.execute(text("DELETE FROM users WHERE email = :e"), {"e": DEMO_CUSTOMER["email"]})

    db.commit()

    print("Old data cleaned.")


def create_categories(db, categories_data):
    print(f"Seeding {len(categories_data)} categories...")

    category_map = {}

    for category_data in categories_data:
        key = category_data.get("key")
        name = category_data.get("name")
        description = category_data.get("description", "")

        if not key:
            raise ValueError(f"Category key missing: {category_data}")

        if not name:
            raise ValueError(f"Category name missing: {category_data}")

        category = Category(
            name=name,
            description=description,
        )

        db.add(category)
        db.commit()
        db.refresh(category)

        category_map[key] = category

    print("Categories seeded.")
    return category_map


def get_category_key(product_data):
    """
    Finds the product's category key.
    Most accurate expected field: categoryKey

    But also supports other naming conventions if present in JSON:
    category_key
    category
    """
    return get_value(
        product_data,
        "categoryKey",
        "category_key",
        "category",
        default=None,
    )


def normalize_stock_status(stock, stock_status):
    if stock_status:
        return stock_status

    if stock <= 0:
        return "out_of_stock"

    if stock < 15:
        return "low_stock"

    return "in_stock"


def create_products(db, products_data, category_map):
    print(f"Seeding {len(products_data)} products from JSON...")

    products = []

    for index, product_data in enumerate(products_data, start=1):
        category_key = get_category_key(product_data)

        if not category_key:
            raise ValueError(
                f"CategoryKey missing in product {index}. "
                f"Product: {product_data.get('name')}"
            )

        category = category_map.get(category_key)

        if not category:
            raise ValueError(
                f"Category not found for product {index}. "
                f"categoryKey={category_key}, product={product_data.get('name')}"
            )

        name = get_value(product_data, "name")

        if not name:
            raise ValueError(f"Name missing in product {index}: {product_data}")

        price = get_value(product_data, "price", default=0)
        original_price = get_value(
            product_data,
            "originalPrice",
            "original_price",
            default=None,
        )

        stock = get_value(product_data, "stock", default=0)
        stock_status = get_value(
            product_data,
            "stockStatus",
            "stock_status",
            default=None,
        )

        stock_status = normalize_stock_status(stock, stock_status)

        # IMPORTANT:
        # We are not using the image field from the JSON.
        # Because currently only 3 images are available.
        # We randomly assign one of these 3 images to each product.
        images = [random.choice(IMAGES_POOL)]

        product = Product(
            name=name,
            model=get_value(product_data, "model", "subType", "sub_type", default=None),
            serial_no=get_value(
                product_data,
                "serialNumber",
                "serial_no",
                "serialNo",
                default=None,
            ),
            description=get_value(product_data, "description", default=""),
            stock=stock,
            price=price,
            warranty=get_value(
                product_data,
                "warrantyStatus",
                "warranty_status",
                "warranty",
                default=None,
            ),
            distributor=get_value(product_data, "distributor", default=None),
            brand=get_value(product_data, "brand", default="SUpplements"),
            sub_type=get_value(
                product_data,
                "model",
                "subType",
                "sub_type",
                default=None,
            ),
            category_id=category.id,
            # Discount comes from JSON.
            # If original_price exists, the product appears as discounted.
            # Otherwise it remains None.
            original_price=original_price,
            rating=get_value(product_data, "rating", default=0.0),
            review_count=get_value(
                product_data,
                "reviewCount",
                "review_count",
                default=0,
            ),
            stock_status=stock_status,
            is_new=get_value(
                product_data,
                "isNew",
                "is_new",
                default=False,
            ),
            images=images,
            tags_json=get_value(
                product_data,
                "tags",
                "tagsJson",
                "tags_json",
                default=[],
            ),
            flavors_json=get_value(
                product_data,
                "flavors",
                "flavorsJson",
                "flavors_json",
                default=[],
            ),
            sizes_json=get_value(
                product_data,
                "sizes",
                "sizesJson",
                "sizes_json",
                default=[],
            ),
            features=get_value(product_data, "features", default=[]),
            ingredients=get_value(product_data, "ingredients", default=""),
            nutrition_facts=get_value(
                product_data,
                "nutritionFacts",
                "nutrition_facts",
                default=None,
            ),
            usage_info=get_value(
                product_data,
                "usageInfo",
                "usage_info",
                default="",
            ),
        )

        products.append(product)

    db.add_all(products)
    db.commit()

    print(f"Products seeded: {len(products)}")
    return products


def get_or_create_demo_review_users(db):
    users = []

    for name, email in DEMO_REVIEW_USERS:
        user = db.query(User).filter(User.email == email).first()

        if user is None:
            user = User(
                name=name,
                email=email,
                password_hash=pwd_context.hash("demo_password"),
                role="customer",
                tax_id="1111111111",
                address="Demo Address",
            )
            db.add(user)
            db.flush()

        users.append(user)

    db.commit()
    return users


def create_demo_reviews(db, products):
    if not products:
        print("No products found. Skipping demo reviews.")
        return

    popular_products = [product for product in products if product.stock > 0][:2]
    if not popular_products:
        popular_products = products[:2]

    users = get_or_create_demo_review_users(db)
    now = datetime.now(timezone.utc)

    reviews = []

    for product_index, product in enumerate(popular_products):
        comment_limit = 10 if product_index == 0 else 5

        for comment_index, (user, comment) in enumerate(
            zip(
                users[:comment_limit],
                DEMO_REVIEW_COMMENTS[:comment_limit],
                strict=True,
            )
        ):
            minute_offset = (
                product_index * len(DEMO_REVIEW_COMMENTS)
            ) + comment_index
            reviews.append(
                Review(
                    product_id=product.id,
                    user_id=user.id,
                    rating=None,
                    comment=comment,
                    approval_status="approved",
                    created_at=now - timedelta(minutes=minute_offset),
                )
            )

    db.add_all(reviews)
    db.commit()

    print(
        f"Demo reviews seeded: {len(reviews)} approved comments "
        f"for product_ids={[product.id for product in popular_products]}."
    )


def create_managers(db):
    print("Seeding manager accounts...")

    managers = [
        {
            "name": "Product Manager",
            "email": os.getenv("PM_EMAIL", "pm@example.com"),
            "password": os.getenv("PM_PASSWORD", "pm_password"),
            "tax_id": os.getenv("PM_TAX_ID", "1234567890"),
            "address": os.getenv("PM_ADDRESS", "PM Office"),
            "role": "product_manager",
        },
        {
            "name": "Sales Manager",
            "email": os.getenv("SM_EMAIL", "sales@example.com"),
            "password": os.getenv("SM_PASSWORD", "sales_password"),
            "tax_id": os.getenv("SM_TAX_ID", "0000000000"),
            "address": os.getenv("SM_ADDRESS", "Sales Office"),
            "role": "sales_manager",
        },
    ]

    for m in managers:
        user = User(
            name=m["name"],
            email=m["email"],
            password_hash=pwd_context.hash(m["password"]),
            tax_id=m["tax_id"],
            address=m["address"],
            role=m["role"],
        )
        db.add(user)

    db.commit()
    print("Manager accounts seeded.")


def create_demo_customer(db) -> User:
    print("Seeding demo customer...")

    customer = User(
        name=DEMO_CUSTOMER["name"],
        email=DEMO_CUSTOMER["email"],
        password_hash=pwd_context.hash(DEMO_CUSTOMER["password"]),
        tax_id=DEMO_CUSTOMER["tax_id"],
        address=DEMO_CUSTOMER["address"],
        role="customer",
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)

    print(f"Demo customer seeded: {customer.email}")
    return customer


def create_demo_efgh_products(db, category_map: dict) -> list:
    print("Seeding demo products E/F/G/H...")

    categories = list(category_map.values())
    cat = lambda key: category_map.get(key, categories[0])  # noqa: E731

    specs = [
        # E: delivered >30 days ago — customer can review it, but refund is blocked
        {
            "name": "Product E",
            "serial_no": "DEMO-E-001",
            "price": Decimal("249.99"),
            "stock": 5,
            "category": cat("saglik"),
            "description": "Demo product E — purchased over 30 days ago.",
        },
        # F: delivered <30 days ago — refund allowed; stock visibly increases after approval
        {
            "name": "Product F",
            "serial_no": "DEMO-F-001",
            "price": Decimal("199.99"),
            "stock": 5,
            "category": cat("protein"),
            "description": "Demo product F — purchased within 30 days, eligible for refund.",
        },
        # G: processing — cancellation is available at this stage
        {
            "name": "Product G",
            "serial_no": "DEMO-G-001",
            "price": Decimal("149.99"),
            "stock": 10,
            "category": cat("vitamin"),
            "description": "Demo product G — order currently in processing.",
        },
        # H: in_transit — shows delivery status flow
        {
            "name": "Product H",
            "serial_no": "DEMO-H-001",
            "price": Decimal("99.99"),
            "stock": 10,
            "category": cat("amino"),
            "description": "Demo product H — order currently in transit.",
        },
    ]

    products = []
    for s in specs:
        p = Product(
            name=s["name"],
            serial_no=s["serial_no"],
            description=s["description"],
            price=s["price"],
            stock=s["stock"],
            stock_status="in_stock",
            brand="SUpplements",
            category_id=s["category"].id,
            images=[random.choice(IMAGES_POOL)],
            tags_json=[],
            flavors_json=[],
            sizes_json=[],
            features=[],
        )
        db.add(p)
        products.append(p)

    db.commit()
    for p in products:
        db.refresh(p)

    print(f"Demo products E/F/G/H seeded: {[p.name for p in products]}")
    return products


def create_demo_orders(db, customer: User, efgh_products: list) -> None:
    print("Seeding demo orders...")

    now = datetime.now(timezone.utc)

    # E: delivered, >30 days ago → review allowed, refund blocked by 30-day window
    # F: delivered, <30 days ago → refund allowed
    # G: processing             → cancellation available
    # H: in_transit             → status display only
    order_specs = [
        {"label": "E", "product": efgh_products[0], "status": "delivered",  "days_ago": 35},
        {"label": "F", "product": efgh_products[1], "status": "delivered",  "days_ago": 10},
        {"label": "G", "product": efgh_products[2], "status": "processing", "days_ago": 2},
        {"label": "H", "product": efgh_products[3], "status": "in_transit", "days_ago": 5},
    ]

    for spec in order_specs:
        product = spec["product"]
        price = product.price if product.price is not None else Decimal("99.99")
        created_at = now - timedelta(days=spec["days_ago"])

        order = Order(
            user_id=customer.id,
            delivery_address=customer.address,
            status=spec["status"],
            total=price,
            created_at=created_at,
        )
        db.add(order)
        db.flush()  # populate order.id before creating invoice

        db.add(OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=1,
            price=price,
        ))

        db.add(Payment(
            order_id=order.id,
            card_last4="1234",
            card_brand="Visa",
            status="success",
            created_at=created_at,
        ))

        db.add(Invoice(
            order_id=order.id,
            invoice_number=f"INV-2026-{order.id:05d}",
            total=price,
            created_at=created_at,
        ))

        print(
            f"  Order {spec['label']}: product='{product.name[:35]}', "
            f"status={spec['status']}, date={created_at.date()}, "
            f"invoice=INV-2026-{order.id:05d}"
        )

    db.commit()
    print("Demo orders seeded.")


def create_demo_wishlist(db, customer: User, products: list) -> None:
    print("Seeding demo wishlist...")

    db.add(WishlistItem(
        user_id=customer.id,
        product_id=products[2].id,
    ))
    db.commit()

    print(f"Wishlist seeded: '{products[2].name[:40]}' added for {customer.email}.")


def validate_seed_data(data):
    categories = data["categories"]
    products = data["products"]

    category_keys = {category["key"] for category in categories}

    print(f"Loaded {len(products)} products.")

    for index, product in enumerate(products, start=1):
        category_key = get_category_key(product)

        if category_key not in category_keys:
            raise ValueError(
                f"Product {index} has an invalid categoryKey value. "
                f"categoryKey={category_key}, product={product.get('name')}"
            )

    print("Seed data validation passed.")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


def seed_db():
    db = SessionLocal()

    try:
        data = load_seed_data()
        validate_seed_data(data)

        clean_old_data(db)

        category_map = create_categories(db, data["categories"])
        products = create_products(db, data["products"], category_map)

        for product, letter in zip(products, ["A", "B", "C"]):
            product.name = f"Product {letter}"
        db.commit()

        create_demo_reviews(db, products)

        create_managers(db)
        customer = create_demo_customer(db)
        efgh_products = create_demo_efgh_products(db, category_map)
        create_demo_orders(db, customer, efgh_products)

        pm_email = os.getenv("PM_EMAIL", "pm@example.com")
        pm_password = os.getenv("PM_PASSWORD", "pm_password")
        sm_email = os.getenv("SM_EMAIL", "sales@example.com")
        sm_password = os.getenv("SM_PASSWORD", "sales_password")

        print(
            f"\n✅ DB ready for demo.\n"
            f"\n  Customer:        {DEMO_CUSTOMER['email']} / {DEMO_CUSTOMER['password']}"
            f"\n  Product Manager: {pm_email} / {pm_password}"
            f"\n  Sales Manager:   {sm_email} / {sm_password}"
            f"\n\n  Catalog products:"
            f"\n    A={products[0].name[:35]} (stock={products[0].stock})"
            f"\n    B={products[1].name[:35]} (stock={products[1].stock})"
            f"\n    C={products[2].name[:35]} (stock={products[2].stock})"
            f"\n    E=Product E  F=Product F  G=Product G  H=Product H"
            f"\n  Orders: E(delivered >30d), F(delivered <10d), G(processing), H(in_transit)"
            f"\n  Wishlist: Product C in customer wishlist\n"
        )

    except Exception as error:
        print(f"❌ Error seeding database: {error}")
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
