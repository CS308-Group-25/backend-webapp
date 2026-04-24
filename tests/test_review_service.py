from unittest.mock import MagicMock

from modules.reviews.model import Review
from modules.reviews.service import ReviewService


def test_submit_review_accepted():
    mock_repo = MagicMock()

    mock_review = MagicMock(spec=Review)
    mock_review.id = 1
    mock_review.user_id = 7
    mock_review.product_id = 42
    mock_review.rating = 4
    mock_review.comment = "Great product"
    mock_review.approval_status = "pending"
    mock_repo.create.return_value = mock_review

    service = ReviewService(mock_repo)
    result = service.submit_review(
        user_id=7, product_id=42, rating=4, comment="Great product"
    )

    assert result.id == 1
    assert result.rating == 4
    mock_repo.create.assert_called_once_with(
        user_id=7, product_id=42, rating=4, comment="Great product"
    )


def test_submit_review_defaults_to_pending():
    mock_repo = MagicMock()

    mock_review = MagicMock(spec=Review)
    mock_review.approval_status = "pending"
    mock_repo.create.return_value = mock_review

    service = ReviewService(mock_repo)
    result = service.submit_review(user_id=1, product_id=1, rating=5, comment=None)

    assert result.approval_status == "pending"


def test_get_approved_reviews_returns_only_approved():
    mock_repo = MagicMock()

    approved = MagicMock(spec=Review)
    approved.approval_status = "approved"
    mock_repo.get_approved_by_product.return_value = [approved]

    service = ReviewService(mock_repo)
    results = service.get_approved_reviews(product_id=10)

    assert len(results) == 1
    assert results[0].approval_status == "approved"
    mock_repo.get_approved_by_product.assert_called_once_with(10)
