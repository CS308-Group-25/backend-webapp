from sqlalchemy.orm import Session

from modules.products.model import Product
from modules.products.repository import ProductRepository
from modules.products.schema import ProductCreate


class ProductService:
    def __init__(self, db: Session):
        self.repository = ProductRepository(db)

    def create_product(self, product_in: ProductCreate) -> Product:
        product_data = product_in.model_dump()
        return self.repository.create_product(product_data)

    def get_product(self, product_id: int) -> Product | None:
        return self.repository.get_by_id(product_id)
      