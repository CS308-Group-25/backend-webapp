from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from modules.auth.model import User
from modules.auth.repository import UserRepository
from modules.auth.schema import LoginRequest, RegisterRequest, UserPublicResponse
from modules.auth.service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", response_model=UserPublicResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    service = AuthService(repo)
    return service.register(data)

@router.post("/login", response_model=UserPublicResponse)
def login(data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    service = AuthService(repo)
    token, user = service.login(data)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
    )
    return user

@router.post("/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie(key="access_token")

@router.get("/me", response_model=UserPublicResponse)
def me(current_user: User = Depends(get_current_user)):
    return UserPublicResponse.model_validate(current_user)