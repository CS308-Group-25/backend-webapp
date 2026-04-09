from fastapi import HTTPException

from modules.products.model import Product
from modules.products.repository import ProductRepository
from modules.products.schema import ProductCreate, ProductUpdate


class ProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    def list_products(self, search: str | None = None, sort: str | None = None,
                      ) -> list[Product]:
                      return self.repo.get_all(search=search, sort=sort)   

    def get_product(self, product_id: int) -> Product:
        product = self.repo.get_by_id(product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return product

    def create_product(self, product_in: ProductCreate) -> Product:
        product_data = product_in.model_dump()
        
        return self.repo.create_product(product_data)

    def update_product(self, product_id: int, product_in: "ProductUpdate") -> Product:
        product = self.get_product(product_id) # Raises 404 if not found
        update_data = product_in.model_dump(exclude_unset=True)
        return self.repo.update_product(product, update_data)

    def delete_product(self, product_id: int) -> None:
        product = self.get_product(product_id)
        self.repo.soft_delete_product(product)
