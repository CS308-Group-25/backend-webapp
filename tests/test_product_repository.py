from unittest.mock import MagicMock

from modules.products.model import Product
from modules.products.repository import ProductRepository


def test_repo_create_product():
    mock_db = MagicMock()
    repo = ProductRepository(mock_db)
    
    product_data = {"name": "Test Product"}
    result = repo.create_product(product_data)
    
    assert result.name == "Test Product"
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
    # Mocking the query chain: db.query().filter().all()
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.all.return_value = []
    
    repo = ProductRepository(mock_db)
    repo.get_all()
    
    # Ensure query uses filter
    mock_db.query.assert_called_once_with(Product)
    mock_query.filter.assert_called_once()
    # Extract the filter condition passed to .filter()
    filter_arg = mock_query.filter.call_args[0][0]
    # We can inspect the SQL string representation of the condition
    assert "deleted_at IS NULL" in str(filter_arg)
