from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from modules.reviews.model import Review
from modules.reviews.service import ReviewService


def test_submit_rating_is_approved_immediately():
    mock_repo = MagicMock()

    mock_review = MagicMock(spec=Review)
    mock_review.id = 1
    mock_review.user_id = 7
    mock_review.product_id = 42
    mock_review.rating = 4
    mock_review.comment = None
    mock_review.approval_status = "approved"
    mock_repo.upsert_rating.return_value = mock_review

    service = ReviewService(mock_repo)
    result = service.submit_review(user_id=7, product_id=42, rating=4, comment=None)

    assert result.id == 1
    assert result.rating == 4
    assert result.approval_status == "approved"
    mock_repo.upsert_rating.assert_called_once_with(
        user_id=7, product_id=42, rating=4
    )


def test_submit_comment_defaults_to_pending():
    mock_repo = MagicMock()

    mock_review = MagicMock(spec=Review)
    mock_review.rating = None
    mock_review.comment = "Great product"
    mock_review.approval_status = "pending"
    mock_repo.create_comment.return_value = mock_review

    service = ReviewService(mock_repo)
    result = service.submit_review(
        user_id=1, product_id=1, rating=None, comment=" Great product "
    )

    assert result.rating is None
    assert result.comment == "Great product"
    assert result.approval_status == "pending"
    mock_repo.create_comment.assert_called_once_with(
        user_id=1, product_id=1, comment="Great product"
    )


def test_submit_review_rejects_combined_rating_and_comment():
    mock_repo = MagicMock()
    service = ReviewService(mock_repo)

    with pytest.raises(HTTPException) as exc:
        service.submit_review(
            user_id=7, product_id=42, rating=4, comment="Great product"
        )

    assert exc.value.status_code == 422
    assert exc.value.detail == "Submit rating and comment separately"
    mock_repo.upsert_rating.assert_not_called()
    mock_repo.create_comment.assert_not_called()


def test_get_approved_reviews_returns_only_approved():
    mock_repo = MagicMock()

    approved = MagicMock(spec=Review)
    approved.id = 1
    approved.product_id = 10
    approved.user_id = 7
    approved.rating = None
    approved.comment = "Great product"
    approved.approval_status = "approved"
    approved.created_at = "2026-05-07T12:00:00"
    approved.user = MagicMock()
    approved.user.name = "Mehmet Er"
    mock_repo.get_approved_by_product.return_value = [approved]

    service = ReviewService(mock_repo)
    results = service.get_approved_reviews(product_id=10)

    assert len(results) == 1
    assert results[0]["approval_status"] == "approved"
    assert results[0]["comment"] == "Great product"
    assert results[0]["customer_name"] == "Mehmet Er"
    mock_repo.get_approved_by_product.assert_called_once_with(10)


def test_approve_review_makes_it_visible():
    mock_repo = MagicMock()

    mock_review = MagicMock(spec=Review)
    mock_review.approval_status = "approved"
    mock_repo.approve.return_value = mock_review

    service = ReviewService(mock_repo)
    result = service.moderate_review(review_id=1, approval_status="approved")

    assert result.approval_status == "approved"
    mock_repo.approve.assert_called_once_with(1)


def test_reject_review_keeps_it_hidden():
    mock_repo = MagicMock()

    mock_review = MagicMock(spec=Review)
    mock_review.approval_status = "rejected"
    mock_repo.reject.return_value = mock_review

    service = ReviewService(mock_repo)
    result = service.moderate_review(review_id=1, approval_status="rejected")

    assert result.approval_status == "rejected"
    mock_repo.reject.assert_called_once_with(1)
