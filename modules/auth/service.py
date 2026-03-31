from fastapi import HTTPException
from passlib.context import CryptContext

from core.security import create_access_token
from modules.auth.repository import UserRepository
from modules.auth.schema import LoginRequest, RegisterRequest, UserPublicResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def register(self, data: RegisterRequest) -> UserPublicResponse:
        existing = self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed = pwd_context.hash(data.password)

        user = self.repo.create_user(
            name=data.name,
            email=data.email,
            password_hash=hashed,
            tax_id=data.tax_id,
            address=data.address,
        )

        return UserPublicResponse.model_validate(user)
    
    def login(self, data: LoginRequest) -> tuple[str, UserPublicResponse]:
        user = self.repo.get_by_email(data.email)
        if not user or not pwd_context.verify(data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = create_access_token({"user_id": user.id, "role": user.role})
        return token, UserPublicResponse.model_validate(user)