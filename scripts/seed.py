import os
import random
import sys

from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from modules.categories.model import Category
from modules.products.model import Product

random.seed(42)  # For reproducible seeding

# ---------------------------------------------------------------------------
# Lookup Tables for Mocks
# ---------------------------------------------------------------------------

CATEGORY_FILTERS = {
    "protein": ["Whey", "Vegan Protein", "Kazein", "İzolat", "Protein Bar"],
    "spor": ["Pre-Workout", "Kreatin", "BCAA", "Gainer", "Enerji Jeli"],
    "vitamin": ["Multivitamin", "B12", "D3", "C Vitamini", "Omega-3"],
    "amino": ["BCAA", "Glutamin", "L-Karnitin", "EAA", "Beta Alanin"],
    "sağlık": ["Probiyotik", "Kolajen", "Çinko", "Magnezyum", "Balık Yağı"],
    "bar": ["Protein Bar", "Enerji Bar", "Granola Bar", "Fıstık Ezmeli", "Brownie"],
    "aksesuar": ["Shaker", "Eldiven", "Kemer", "Çanta", "Bileklik"],
}

CATEGORY_DESCRIPTIONS = {
    "protein": "Kas gelişimi için premium protein tozları.",
    "spor": "Antrenman performansını artıran sporcu gıdaları.",
    "vitamin": "Günlük sağlık ve zindelik için esansiyel vitaminler.",
    "amino": "Hızlı onarım sağlayan saf amino asit formülleri.",
    "sağlık": "Genel vücut sağlığını destekleyen gıda takviyeleri.",
    "bar": "Gün içinde atıştırabileceğiniz protein ve enerji barları.",
    "aksesuar": "Spor salonunda hayatınızı kolaylaştıracak ekipman ve giysiler.",
}

BRANDS = [
    "Optimum Nutrition",
    "MyProtein",
    "BSN",
    "Supplements",
    "Weider",
    "Hardline",
    "Big Joy",
    "GymWear",  # For accessories
    "ProGear",  # For accessories
]

FLAVORS_POOL = [
    {"id": "choc", "name": "Çikolata", "color": "#5C3317"},
    {"id": "van", "name": "Vanilya", "color": "#F3E5AB"},
    {"id": "straw", "name": "Çilek", "color": "#E8474C"},
    {"id": "biscuit", "name": "Bisküvi", "color": "#D2A679"},
    {"id": "banana", "name": "Muz", "color": "#FFE135"},
    {"id": "caramel", "name": "Salted Caramel", "color": "#C68E4E"},
    {"id": "unflavored", "name": "Aromasız", "color": "#E5E7EB"},
    {"id": "mango", "name": "Mango", "color": "#F59E0B"},
]

COLORS_POOL = [
    {"id": "black", "name": "Siyah", "color": "#000000"},
    {"id": "white", "name": "Beyaz", "color": "#FFFFFF"},
    {"id": "red", "name": "Kırmızı", "color": "#EF4444"},
    {"id": "blue", "name": "Mavi", "color": "#3B82F6"},
    {"id": "grey", "name": "Gri", "color": "#9CA3AF"},
]

TAGS_POOL = [
    "Vegan",
    "Glutensiz",
    "Vejetaryen",
    "Şeker İlavesiz",
    "Organik",
    "Helal",
    "Yeni Tasarım",
    "Ergonomik",
]

IMAGES_POOL = [
    "/products/bcaa.png",
    "/products/creatine.png",
    "/products/protein-bar.png",
]

DESCRIPTIONS_POOL = [
    "Hedeflerinize ulaşmanızı sağlayacak yüksek kaliteli bir ürün.",
    "Performans ve onarım için dizayn edilmiş premium bir seçenek.",
    "Günlük ihtiyacınızı karşılamaya yardımcı olan destekleyicidir.",
    "Spor öncesi ve sonrasında en iyi yardımcınız. Performansınızı artırır.",
    "İhtiyaç duyduğunuz temel özellikleri barındıran kompleks yapı.",
]

FEATURES_POOL = [
    "Yüksek biyoyararlanım veya verimlilik sağlar.",
    "Kolay kullanım ve pratik taşınabilirlik.",
    "Premium materyallerden ve hammaddelerden üretilmiştir.",
    "Günlük egzersiz rutininizi doğrudan destekler.",
    "Modern çizgisi ve fonksiyonelliğiyle öne çıkar.",
]

INGREDIENTS_POOL = [
    "Whey protein izolatı, aroma vericiler, sukraloz, ayçiçek lesitini.",
    "L-sitrülin, Beta alanin, B vitaminleri kompleksi, tatlandırıcı.",
    "Magnezyum sitrat, Çinko pikolinat, B6 vitamini, hacim artırıcı.",
    "Kreatin monohidrat (%100 saf), aromasız.",
    "Misel kazein proteini, kakao tozu, kıvam artırıcı (ksantan gam).",
]


def seed_db():
    db = SessionLocal()

    try:
        print("Cleaning old data to prevent conflicts...")
        db.execute(text("DELETE FROM cart_items"))
        db.execute(text("DELETE FROM order_items"))
        if "Review" in sys.modules:
            try:
                db.execute(text("DELETE FROM reviews"))
            except Exception:
                pass

        db.query(Product).delete()
        db.query(Category).delete()
        db.commit()

        print("Seeding 7 exact categories...")
        db_categories = {}

        # We define them exactly matching the frontend filter keys
        for key, description in CATEGORY_DESCRIPTIONS.items():
            cat = Category(name=key.capitalize(), description=description)
            db.add(cat)
            db.commit()
            db.refresh(cat)
            db_categories[key] = cat

        products = []
        print("Seeding 110 rich products covering all 7 categories...")

        for _ in range(110):
            # Pick a random category filter key
            filter_key = random.choice(list(CATEGORY_FILTERS.keys()))
            cat = db_categories[filter_key]

            sub_type = random.choice(CATEGORY_FILTERS[filter_key])

            # Accessories are more likely to have sports brands
            if filter_key == "aksesuar":
                brand = random.choice(["GymWear", "ProGear", "Supplements"])
            else:
                brand = random.choice(BRANDS[:7])

            # Pricing logic
            price = round(random.uniform(99, 1499), 2)
            has_discount = random.choice([True, False, False])
            original_price = (
                round(price * random.uniform(1.2, 1.5), 2) if has_discount else None
            )

            # Stock logic
            stock = random.randint(0, 300)
            stock_status = "in_stock"
            if stock == 0:
                stock_status = "out_of_stock"
            elif stock < 15:
                stock_status = "low_stock"

            # Logic branches depending on if it is an accessory or not
            is_accessory = filter_key == "aksesuar"

            # Frontend uses the "flavors" prop to render the color pickers
            if is_accessory:
                flavors = random.sample(COLORS_POOL, k=random.randint(1, 3))
                sizes = [
                    {
                        "id": "sizem",
                        "label": "M Beden",
                        "price": price,
                        "originalPrice": original_price,
                    },
                    {
                        "id": "sizel",
                        "label": "L Beden",
                        "price": price,
                        "originalPrice": original_price,
                    },
                ]
                nutrition_facts = None
                ingredients = "Yüksek kaliteli sporcu kumaşı / materyali."
                usage_info = "Elde veya çamaşır makinesinde 30 derecede yıkayınız."
                tags = random.sample(["Yeni Tasarım", "Ergonomik", "Vegan"], k=2)
            else:
                flavors = random.sample(FLAVORS_POOL, k=random.randint(1, 4))
                sizes = [
                    {
                        "id": f"s_{random.randint(100, 500)}",
                        "label": f"{random.randint(200, 1000)}g",
                        "servings": random.randint(20, 60),
                        "price": price,
                        "originalPrice": original_price,
                    }
                ]
                nutrition_facts = [
                    {
                        "label": "Enerji",
                        "perServing": f"{random.randint(0, 150)} kcal",
                        "per100g": f"{random.randint(200, 400)} kcal",
                    },
                    {
                        "label": "Protein",
                        "perServing": f"{random.randint(0, 30)}g",
                        "per100g": f"{random.randint(10, 90)}g",
                    },
                    {
                        "label": "Karbonhidrat",
                        "perServing": f"{random.randint(0, 50)}g",
                        "per100g": f"{random.randint(0, 100)}g",
                    },
                    {
                        "label": "Yağ",
                        "perServing": f"{random.uniform(0.1, 5.0):.1f}g",
                        "per100g": f"{random.uniform(1.0, 15.0):.1f}g",
                    },
                ]
                ingredients = random.choice(INGREDIENTS_POOL)
                usage_info = (
                    "1 ölçek (veya porsiyon) ürünü 250ml su ile karıştırıp tüketiniz."
                )
                tags = random.sample(TAGS_POOL[:6], k=random.randint(0, 3))

            images = random.sample(IMAGES_POOL, k=random.randint(1, len(IMAGES_POOL)))
            features = random.sample(FEATURES_POOL, k=random.randint(2, 4))

            product = Product(
                name=f"{brand} {sub_type}",
                description=random.choice(DESCRIPTIONS_POOL),
                stock=stock,
                price=price,
                brand=brand,
                category_id=cat.id,
                # --- Rich Fields for Frontend Mock ---
                original_price=original_price,
                rating=round(random.uniform(4.0, 5.0), 1) if stock > 0 else 0,
                review_count=random.randint(0, 2500) if stock > 0 else 0,
                stock_status=stock_status,
                is_new=random.choice([True, False, False, False]),
                images=images,
                tags_json=tags,
                flavors_json=flavors,
                sizes_json=sizes,
                features=features,
                ingredients=ingredients,
                nutrition_facts=nutrition_facts,
                usage_info=usage_info,
            )
            products.append(product)

        db.add_all(products)
        db.commit()
        print(f"Successfully seeded DB with 7 categories and {len(products)} products!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
