from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user, require_product_manager
from modules.auth.model import User
from modules.reviews.repository import ReviewRepository
from modules.reviews.schema import ReviewCreate, ReviewModerationRequest, ReviewResponse, ReviewAdminResponse
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

admin_router = APIRouter(prefix="/api/v1/admin/reviews", tags=["admin-reviews"])


@admin_router.get("", response_model=list[ReviewAdminResponse])
def list_reviews(
    status: str | None = None,
    current_user: User = Depends(require_product_manager),
    service: ReviewService = Depends(get_review_service),
):
    return service.list_reviews(status)


@admin_router.patch("/{review_id}", response_model=ReviewAdminResponse)
def moderate_review(
    review_id: int,
    data: ReviewModerationRequest,
    current_user: User = Depends(require_product_manager),
    service: ReviewService = Depends(get_review_service),
):
    return service.moderate_review(review_id, data.approval_status)


@admin_router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    current_user: User = Depends(require_product_manager),
    service: ReviewService = Depends(get_review_service),
):
    service.delete_review(review_id)
