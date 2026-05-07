from sqlalchemy.orm import Session

from modules.reviews.model import Review


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert_rating(
        self,
        user_id: int,
        product_id: int,
        rating: int,
    ) -> Review:
        review = (
            self.db.query(Review)
            .filter(Review.user_id == user_id)
            .filter(Review.product_id == product_id)
            .filter(Review.rating.is_not(None))
            .filter(Review.comment.is_(None))
            .first()
        )

        if review:
            review.rating = rating
            review.approval_status = "approved"
        else:
            review = Review(
                user_id=user_id,
                product_id=product_id,
                rating=rating,
                comment=None,
                approval_status="approved",
            )
            self.db.add(review)

        self.db.commit()
        self.db.refresh(review)
        return review

    def create_comment(self, user_id: int, product_id: int, comment: str) -> Review:
        review = Review(
            user_id=user_id,
            product_id=product_id,
            rating=None,
            comment=comment,
            approval_status="pending",
        )
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def get_approved_by_product(self, product_id: int) -> list[Review]:
        return (
            self.db.query(Review)
            .filter(Review.product_id == product_id)
            .filter(Review.approval_status == "approved")
            .filter(Review.comment.is_not(None))
            .all()
        )

    def get_all_by_status(self, status: str | None = None) -> list[Review]:
        query = self.db.query(Review).filter(Review.comment.is_not(None))
        if status:
            query = query.filter(Review.approval_status == status)
        return query.order_by(Review.created_at.desc()).all()

    def approve(self, review_id: int) -> Review | None:
        review = self.db.query(Review).filter(Review.id == review_id).first()
        if review is None:
            return None
        review.approval_status = "approved"
        self.db.commit()
        self.db.refresh(review)
        return review

    def reject(self, review_id: int) -> Review | None:
        review = self.db.query(Review).filter(Review.id == review_id).first()
        if review is None:
            return None
        review.approval_status = "rejected"
        self.db.commit()
        self.db.refresh(review)
        return review

    def delete(self, review_id: int) -> bool:
        review = self.db.query(Review).filter(Review.id == review_id).first()
        if review is None:
            return False
        self.db.delete(review)
        self.db.commit()
        return True
