from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import decode_access_token
from modules.auth.model import User
from modules.auth.repository import UserRepository


def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    payload = decode_access_token(access_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ("product_manager", "sales_manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def require_product_manager(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "product_manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only product managers can perform this action",
        )
    return current_user
    