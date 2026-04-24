from fastapi import HTTPException

from modules.reviews.model import Review
from modules.reviews.repository import ReviewRepository


class ReviewService:
    def __init__(self, repo: ReviewRepository):
        self.repo = repo

    def list_reviews(self, status: str | None = None) -> list:
        reviews = self.repo.get_all_by_status(status)
        result = []
        for r in reviews:
            result.append({
                "id": r.id,
                "product_id": r.product_id,
                "user_id": r.user_id,
                "rating": r.rating,
                "comment": r.comment,
                "approval_status": r.approval_status,
                "created_at": r.created_at,
                "product_name": r.product.name if r.product else None,
                "customer_name": r.user.name if r.user else None,
                "customer_email": r.user.email if r.user else None,
            })
        return result

    def get_approved_reviews(self, product_id: int) -> list[Review]:
        return self.repo.get_approved_by_product(product_id)

    def submit_review(
        self, user_id: int, product_id: int, rating: int, comment: str | None
    ) -> Review:
        if rating < 1 or rating > 5:
            raise HTTPException(
                status_code=422, detail="Rating must be between 1 and 5"
            )
        return self.repo.create(
            user_id=user_id,
            product_id=product_id,
            rating=rating,
            comment=comment,
        )
    
    def moderate_review(self, review_id: int, approval_status: str) -> Review:
        if approval_status == "approved":
            review = self.repo.approve(review_id)
        else:
            review = self.repo.reject(review_id)
        if review is None:
            raise HTTPException(status_code=404, detail="Review not found")
        return review

    def delete_review(self, review_id: int) -> None:
        deleted = self.repo.delete(review_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Review not found")

