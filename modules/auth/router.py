from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from modules.auth.repository import UserRepository
from modules.auth.schema import RegisterRequest, UserPublicResponse
from modules.auth.service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", response_model=UserPublicResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    service = AuthService(repo)
    return service.register(data)
