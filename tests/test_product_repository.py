from unittest.mock import MagicMock

from modules.products.model import Product
from modules.products.repository import ProductRepository


def test_repo_create_product():
    mock_db = MagicMock()
    repo = ProductRepository(mock_db)

    product_data = {
        "name": "Whey Protein",
        "model": "Gold Standard",
        "serial_no": "WHEY-123",
        "description": "High quality protein",
        "stock": 100,
        "warranty": "2 years",
        "distributor": "Optimum Nutrition",
        "brand": "ON",
        "flavor": "Chocolate",
        "form": "Powder",
        "serving_size": "30g",
        "goal_tags": "muscle-gain,recovery",
        "category_id": 1,
    }
    result = repo.create_product(product_data)

    assert result.name == "Whey Protein"
    assert result.model == "Gold Standard"
    assert result.serial_no == "WHEY-123"
    assert result.stock == 100
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_repo_soft_delete_sets_deleted_at():
    mock_db = MagicMock()
    repo = ProductRepository(mock_db)

    db_product = Product(id=1, name="Test")
    result = repo.soft_delete_product(db_product)

    # We now use datetime.now(timezone.utc)
    from datetime import datetime

    assert isinstance(result.deleted_at, datetime)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_repo_get_all_excludes_deleted():
    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_filter = MagicMock()

    # Setup the chain: db.query(Product).filter(...)
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter

    # Mock return values for pagination/counting
    mock_filter.count.return_value = 0
    mock_filter.offset.return_value.limit.return_value.all.return_value = []

    repo = ProductRepository(mock_db)
    repo.get_all()

    # Verify the filter was applied correctly
    mock_db.query.assert_called_with(Product)
    mock_query.filter.assert_called()

    # Verify that the filter condition targets the deleted_at column
    filter_arg = mock_query.filter.call_args[0][0]
    # In SQLAlchemy, Product.deleted_at.is_(None) evaluates to a binary expression
    assert "deleted_at" in str(filter_arg)
    assert "IS NULL" in str(filter_arg).upper()
