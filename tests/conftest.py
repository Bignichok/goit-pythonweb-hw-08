import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from typing import Generator

# Set testing environment
os.environ["TESTING"] = "True"
os.environ["SECRET_KEY"] = "test_secret_key_123"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["REFRESH_TOKEN_EXPIRE_DAYS"] = "7"
os.environ["SMTP_SERVER"] = "smtp.gmail.com"
os.environ["SMTP_PORT"] = "587"
os.environ["SMTP_USERNAME"] = "test@gmail.com"
os.environ["SMTP_PASSWORD"] = "test_password"
os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"
os.environ["REDIS_PASSWORD"] = "test_password"
os.environ["CLOUDINARY_CLOUD_NAME"] = "test_cloud"
os.environ["CLOUDINARY_API_KEY"] = "test_api_key"
os.environ["CLOUDINARY_API_SECRET"] = "test_api_secret"

# Mock the database creation before importing app
with patch("sqlalchemy.create_engine"), \
     patch("sqlalchemy.orm.sessionmaker"), \
     patch("app.core.database.Base.metadata.create_all"):
    from app.main import app
    from app.core.config import settings
    from app.core.database import get_db

@pytest.fixture
def mock_db() -> Generator:
    """Fixture that returns a mock database session."""
    mock = MagicMock()
    yield mock

@pytest.fixture
def client(mock_db) -> TestClient:
    """Fixture that returns test client with mocked db dependency."""
    def override_get_db():
        try:
            yield mock_db
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db] 