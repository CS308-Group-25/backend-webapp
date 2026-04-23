from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from modules.categories.repository import CategoryRepository
from modules.categories.schema import CategoryResponse
from modules.categories.service import CategoryService

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    repo = CategoryRepository(db)
    service = CategoryService(repo)

    return service.list_categories()
