from sqlalchemy.orm import Session

from modules.categories.model import Category, SubCategory
from modules.products.model import Product


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Category]:
        return self.db.query(Category).all()

    def get_by_id(self, category_id: int) -> Category | None:
        return self.db.query(Category).filter(Category.id == category_id).first()

    def get_by_name(self, name: str) -> Category | None:
        return self.db.query(Category).filter(Category.name == name).first()

    def create(self, category_data: dict) -> Category:
        category = Category(**category_data)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def update(self, category: Category, update_data: dict) -> Category:
        for key, value in update_data.items():
            setattr(category, key, value)
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, category: Category) -> None:
        self.db.delete(category)
        self.db.commit()

    def get_all_sub_categories(self) -> list[dict]:
        from sqlalchemy import func
        result = (
            self.db.query(SubCategory, Category.name, func.count(Product.id))
            .join(Category, SubCategory.category_id == Category.id)
            .outerjoin(Product, Product.sub_type == SubCategory.name)
            .group_by(SubCategory.id, Category.name)
            .all()
        )
        sub_categories = []
        for sub_cat, cat_name, prod_count in result:
            sub_categories.append({
                "id": sub_cat.id,
                "name": sub_cat.name,
                "description": sub_cat.description,
                "category_id": sub_cat.category_id,
                "categoryName": cat_name,
                "productCount": prod_count
            })
        return sub_categories

    def get_sub_category_by_id(self, sub_id: int) -> SubCategory | None:
        return self.db.query(SubCategory).filter(SubCategory.id == sub_id).first()

    def get_sub_category_by_name(self, name: str) -> SubCategory | None:
        return self.db.query(SubCategory).filter(SubCategory.name == name).first()

    def create_sub_category(self, data: dict) -> SubCategory:
        sub = SubCategory(**data)
        self.db.add(sub)
        self.db.commit()
        self.db.refresh(sub)
        return sub

    def update_sub_category(self, sub: SubCategory, data: dict) -> SubCategory:
        old_name = sub.name
        new_name = data.get("name", old_name)
        old_category_id = sub.category_id
        new_category_id = data.get("category_id", old_category_id)

        for k, v in data.items():
            setattr(sub, k, v)

        updates = {}
        if old_name != new_name:
            updates["sub_type"] = new_name
        if old_category_id != new_category_id:
            updates["category_id"] = new_category_id
        
        if updates:
            self.db.query(Product).filter(Product.sub_type == old_name).update(updates)

        self.db.commit()
        self.db.refresh(sub)
        return sub

    def delete_sub_category(self, sub: SubCategory) -> None:
        self.db.query(Product).filter(Product.sub_type == sub.name).update(
            {"sub_type": None}
        )
        self.db.delete(sub)
        self.db.commit()
