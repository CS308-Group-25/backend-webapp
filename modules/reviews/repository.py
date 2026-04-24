from sqlalchemy.orm import Session

from modules.reviews.model import Review


class ReviewRepository:
  def __init__(self, db: Session):
    self.db=db

  def create(
    self, user_id: int, product_id: int, rating: int, comment: str | None
  ) -> Review:
    review = Review(
      user_id=user_id,
      product_id=product_id,
      rating=rating,
      comment=comment,
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
          .all()
        )
  
  def approve(self, review_id: int) -> Review | None:
    review = self.db.query(Review).filter(Review.id==review_id).first()
    if review is None:
      return None
    review.approval_status = "approved"
    self.db.commit()
    self.db.refresh(review)
    return review
  
  def reject(self, review_id: int)-> Review | None:
    review= self.db.query(Review).filter(Review.id == review_id).first()
    if review is None:
      return None
    review.approval_status="rejected"
    self.db.commit()
    self.db.refresh(review)
    return review
