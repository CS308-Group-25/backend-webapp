from fastapi import HTTPException

from modules.categories.model import Category
from modules.categories.repository import CategoryRepository
from modules.categories.schema import (
    CategoryCreate,
    CategoryUpdate,
    SubCategoryCreate,
    SubCategoryUpdate,
)


class CategoryService:
    def __init__(self, repo: CategoryRepository):
        self.repo = repo

    def list_categories(self) -> list[Category]:
        return self.repo.get_all()

    def create_category(self, data: CategoryCreate) -> Category:
        existing = self.repo.get_by_name(data.name)
        if existing:
            raise HTTPException(
                status_code=400, detail="Category already exists"
            )
        return self.repo.create(data.model_dump())

    def update_category(self, category_id: int, data: CategoryUpdate) -> Category:
        category = self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        if data.name and data.name != category.name:
            existing = self.repo.get_by_name(data.name)
            if existing:
                raise HTTPException(
                    status_code=400, detail="Category name already exists"
                )
        return self.repo.update(category, data.model_dump(exclude_unset=True))

    def delete_category(self, category_id: int) -> None:
        category = self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        self.repo.delete(category)

    def list_sub_categories(self) -> list[dict]:
        return self.repo.get_all_sub_categories()

    def create_sub_category(self, data: SubCategoryCreate):
        existing = self.repo.get_sub_category_by_name(data.name)
        if existing:
            raise HTTPException(status_code=400, detail="SubCategory already exists")
        return self.repo.create_sub_category(data.model_dump())

    def update_sub_category(self, sub_id: int, data: SubCategoryUpdate):
        sub = self.repo.get_sub_category_by_id(sub_id)
        if not sub:
            raise HTTPException(status_code=404, detail="SubCategory not found")
        if data.name and data.name != sub.name:
            existing = self.repo.get_sub_category_by_name(data.name)
            if existing:
                raise HTTPException(
                    status_code=400, detail="SubCategory name already exists"
                )
        return self.repo.update_sub_category(sub, data.model_dump(exclude_unset=True))

    def delete_sub_category(self, sub_id: int) -> None:
        sub = self.repo.get_sub_category_by_id(sub_id)
        if not sub:
            raise HTTPException(status_code=404, detail="SubCategory not found")
        self.repo.delete_sub_category(sub)
