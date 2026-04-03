from fastapi import HTTPException

from modules.products.model import Product
from modules.products.repository import ProductRepository
from modules.products.schema import ProductCreate


class ProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    def list_products(self) -> list[Product]:
        return self.repo.get_all()

    def get_product(self, product_id: int) -> Product:
        product = self.repo.get_by_id(product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return product

    def create_product(self, product_in: ProductCreate) -> Product:
        product_data = product_in.model_dump()
        
        return self.repo.create_product(product_data)
