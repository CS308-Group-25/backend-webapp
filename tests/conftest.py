from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def mock_repo():
    """Generic mock repository for service layer tests"""
    return MagicMock()


@pytest.fixture
def client():
    """FastAPI test client API smoke tests"""
    return TestClient(app)
