from modules.categories.model import Category
from modules.categories.repository import CategoryRepository


class CategoryService:
    def __init__(self, repo: CategoryRepository):
        self.repo = repo

    def list_categories(self) -> list[Category]:
        return self.repo.get_all()