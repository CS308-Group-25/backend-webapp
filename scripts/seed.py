import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from modules.categories.model import Category
from modules.products.model import Product

def seed_db():
    db = SessionLocal()
    
    try:
        
        if db.query(Category).first():
            print("Database already seeded.")
            return

        print("Seeding database...")
        
       
        cat1 = Category(name="Proteins", description="Premium protein powders and supplements")
        cat2 = Category(name="Vitamins", description="Essential vitamins and daily health minerals")
        cat3 = Category(name="Pre-Workouts", description="Energy boosters and pre-workout formulas")
        
        db.add_all([cat1, cat2, cat3])
        db.commit() 
        
        
        db.refresh(cat1)
        db.refresh(cat2)
        db.refresh(cat3)

        
        products = [
            
            Product(name="Whey Protein Isolate", description="100% pure fast-absorbing whey protein", price=49.99, stock=100, category_id=cat1.id),
            Product(name="Casein Protein", description="Slow-digesting nighttime muscle recovery protein", price=45.99, stock=50, category_id=cat1.id),
            Product(name="Plant Protein Blend", description="Vegan friendly pea and brown rice protein", price=39.99, stock=75, category_id=cat1.id),
            Product(name="Mass Gainer", description="High calorie protein formula for bulking", price=55.99, stock=30, category_id=cat1.id),
            
            
            Product(name="Multivitamin Complex", description="Daily essential vitamins for men and women", price=19.99, stock=200, category_id=cat2.id),
            Product(name="Vitamin D3", description="High potency vitamin D3 5000 IU", price=14.99, stock=150, category_id=cat2.id),
            Product(name="Omega 3 Fish Oil", description="Triple strength EPA/DHA joint support", price=24.99, stock=120, category_id=cat2.id),
            
            
            Product(name="Explosive Pre-Workout", description="High stim pre-workout for maximum energy", price=34.99, stock=80, category_id=cat3.id),
            Product(name="Stim-Free Pump", description="Nitric oxide booster for maximum vascularity", price=29.99, stock=60, category_id=cat3.id),
            Product(name="BCAA Energy", description="Branched-chain amino acids with natural caffeine", price=27.99, stock=90, category_id=cat3.id)
        ]
        
        db.add_all(products)
        db.commit()
        print("Successfully seeded the database with 3 categories and 10 products!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()