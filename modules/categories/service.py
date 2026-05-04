from fastapi import HTTPException

from modules.categories.model import Category
from modules.categories.repository import CategoryRepository
from modules.categories.schema import CategoryCreate, CategoryUpdate


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
