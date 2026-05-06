# isort: skip_file

import json
import os
import random
import sys
from pathlib import Path

from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from modules.categories.model import Category
from modules.products.model import Product


random.seed(42)


# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------


# Seed data is stored outside the scripts folder to keep scripts clean.
# Example:
# backend-webapp/seed_data/supplement_store_110_products.json
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

DATA_FILE = PROJECT_ROOT / "seed_data" / "supplement_store_110_products.json"


# Only these 3 images are currently available.
# These files must be located under public/products on the frontend.
IMAGES_POOL = [
    "/products/bcaa.png",
    "/products/creatine.png",
    "/products/protein-bar.png",
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

    tables_to_clean = [
        "cart_items",
        "order_items",
        "wishlist_items",
        "reviews",
    ]

    for table_name in tables_to_clean:
        try:
            db.execute(text(f"DELETE FROM {table_name}"))
        except Exception:
            pass

    db.query(Product).delete()
    db.query(Category).delete()
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
            description=get_value(product_data, "description", default=""),
            stock=stock,
            price=price,
            brand=get_value(product_data, "brand", default="SUpplements"),
            sub_type=get_value(product_data, "subType", "sub_type", default=None),
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


def validate_seed_data(data):
    categories = data["categories"]
    products = data["products"]

    category_keys = {category["key"] for category in categories}

    if len(products) != 110:
        print(
            f"⚠️ Warning: Expected 110 products in JSON, "
            f"but found {len(products)} products."
        )

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
        create_products(db, data["products"], category_map)

        print(
            f"✅ Successfully seeded DB: "
            f"{len(data['categories'])} categories, {len(data['products'])} products."
        )

    except Exception as error:
        print(f"❌ Error seeding database: {error}")
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
