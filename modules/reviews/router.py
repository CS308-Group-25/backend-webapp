from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from modules.auth.model import User
from modules.reviews.repository import ReviewRepository
from modules.reviews.schema import ReviewCreate, ReviewResponse
from modules.reviews.service import ReviewService

router = APIRouter(prefix="/api/v1/products", tags=["reviews"])


def get_review_service(db: Session = Depends(get_db)) -> ReviewService:
    return ReviewService(ReviewRepository(db))


@router.post(
    "/{product_id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_review(
    product_id: int,
    data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service),
):
    return service.submit_review(
        user_id=current_user.id,
        product_id=product_id,
        rating=data.rating,
        comment=data.comment,
    )


@router.get("/{product_id}/reviews", response_model=list[ReviewResponse])
def get_approved_reviews(
    product_id: int,
    service: ReviewService = Depends(get_review_service),
):
    return service.get_approved_reviews(product_id)
