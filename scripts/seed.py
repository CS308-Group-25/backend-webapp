import os
import random
import sys

from faker import Faker
from sqlalchemy import text

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from core.database import SessionLocal
from modules.categories.model import Category
from modules.products.model import Product

random.seed(42)  # For reproducible seeding
faker = Faker('tr_TR')  # Türkçe daha gerçekçi isimler ve textler için

# ---------------------------------------------------------------------------
# Lookup Tables for Mocks
# ---------------------------------------------------------------------------

CATEGORY_FILTERS = {
    "protein": ["Whey", "Vegan Protein", "Kazein", "İzolat", "Protein Bar"],
    "spor":    ["Pre-Workout", "Kreatin", "BCAA", "Gainer", "Enerji Jeli"],
    "vitamin": ["Multivitamin", "B12", "D3", "C Vitamini", "Omega-3"],
}

BRANDS = ["Optimum Nutrition", "MyProtein", "BSN", "Supplements", "Weider", "Hardline", "Big Joy"]

FLAVORS_POOL = [
    {"id": "choc", "name": "Çikolata", "color": "#5C3317"},
    {"id": "van", "name": "Vanilya", "color": "#F3E5AB"},
    {"id": "straw", "name": "Çilek", "color": "#E8474C"},
    {"id": "biscuit", "name": "Bisküvi", "color": "#D2A679"},
    {"id": "banana", "name": "Muz", "color": "#FFE135"},
    {"id": "caramel", "name": "Salted Caramel", "color": "#C68E4E"},
    {"id": "unflavored", "name": "Aromasız", "color": "#E5E7EB"},
    {"id": "mango", "name": "Mango", "color": "#F59E0B"}
]

TAGS_POOL = ["Vegan", "Glutensiz", "Vejetaryen", "Şeker İlavesiz", "Organik", "Helal"]
IMAGES_POOL = ["/products/bcaa.png", "/products/creatine.png", "/products/protein-bar.png"]


def seed_db():
    db = SessionLocal()

    try:
        print("Cleaning old data to prevent conflicts...")
        # Clear dependent tables first
        db.execute(text("DELETE FROM cart_items"))
        db.execute(text("DELETE FROM order_items"))
        if "Review" in sys.modules: 
            # If reviews get created later, theoretically good to clear them if table exists
            try:
                db.execute(text("DELETE FROM reviews"))
            except:
                pass
        
        db.query(Product).delete()
        db.query(Category).delete()
        db.commit()

        print("Seeding categories...")

        cat1 = Category(name="Proteins", description="Premium protein powders and supplements")
        cat2 = Category(name="Vitamins", description="Essential vitamins and daily health minerals")
        cat3 = Category(name="Pre-Workouts", description="Energy boosters and pre-workout formulas")

        db.add_all([cat1, cat2, cat3])
        db.commit()
        db.refresh(cat1)
        db.refresh(cat2)
        db.refresh(cat3)

        cat_filter_map = {
            cat1.id: "protein",
            cat2.id: "vitamin",
            cat3.id: "spor",
        }

        categories = [cat1, cat2, cat3]
        products = []

        print("Seeding 110 rich products...")

        for _ in range(110):
            cat = random.choice(categories)
            filter_key = cat_filter_map[cat.id]
            brand = random.choice(BRANDS)
            sub_type = random.choice(CATEGORY_FILTERS[filter_key])
            
            # Pricing logic
            price = round(random.uniform(99, 1499), 2)
            has_discount = random.choice([True, False, False]) # 33% indirimli
            original_price = round(price * random.uniform(1.2, 1.5), 2) if has_discount else None
            
            # Stock logic
            stock = random.randint(0, 300)
            stock_status = "in_stock"
            if stock == 0:
                stock_status = "out_of_stock"
            elif stock < 15:
                stock_status = "low_stock"
                
            # Random rich properties
            flavors = random.sample(FLAVORS_POOL, k=random.randint(1, 4))
            images = random.sample(IMAGES_POOL, k=random.randint(1, len(IMAGES_POOL)))
            tags = random.sample(TAGS_POOL, k=random.randint(0, 3))
            
            # Base size config
            sizes = [
                {
                    "id": f"s_{random.randint(100, 500)}", 
                    "label": "Standart Boy", 
                    "servings": random.randint(20, 60), 
                    "price": price, 
                    "originalPrice": original_price
                }
            ]
            
            nutrition_facts = [
                {"label": "Enerji", "perServing": f"{random.randint(0,150)} kcal", "per100g": f"{random.randint(200,400)} kcal"},
                {"label": "Protein", "perServing": f"{random.randint(0,30)}g", "per100g": f"{random.randint(10,90)}g"},
                {"label": "Karbonhidrat", "perServing": f"{random.randint(0,50)}g", "per100g": f"{random.randint(0,100)}g"},
                {"label": "Yağ", "perServing": f"{random.uniform(0.1, 5.0):.1f}g", "per100g": f"{random.uniform(1.0, 15.0):.1f}g"}
            ]
            
            features = [
                faker.sentence(nb_words=6) for _ in range(random.randint(3, 5))
            ]
            
            product = Product(
                name=f"{brand} {sub_type}",
                description=faker.paragraph(nb_sentences=2),
                stock=stock,
                price=price,
                brand=brand,
                category_id=cat.id,
                
                # --- Rich Fields for Frontend Mock ---
                original_price=original_price,
                rating=round(random.uniform(4.0, 5.0), 1) if stock > 0 else 0, # ratings
                review_count=random.randint(0, 2500) if stock > 0 else 0,
                stock_status=stock_status,
                is_new=random.choice([True, False, False, False]), # 25% chance of being new
                images=images,
                tags_json=tags,
                flavors_json=flavors,
                sizes_json=sizes,
                features=features,
                ingredients=faker.paragraph(nb_sentences=4),
                nutrition_facts=nutrition_facts,
                usage_info="1 ölçek (30g) ürünü 250ml su ile karıştırıp tüketiniz."
            )
            products.append(product)

        db.add_all(products)
        db.commit()
        print(f"Successfully seeded the database with 3 categories and {len(products)} products!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()