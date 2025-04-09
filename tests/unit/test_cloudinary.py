import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, UploadFile

from app.core.cloudinary import upload_avatar
from app.models.user import User

@pytest.fixture
def mock_user():
    return User(
        id=1,
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_verified=True
    )

@pytest.fixture
def mock_file():
    """Create a mock file for testing."""
    mock = MagicMock(spec=UploadFile)
    mock.filename = "test.jpg"
    mock.content_type = "image/jpeg"
    mock.file = MagicMock()
    return mock

@pytest.mark.asyncio
async def test_upload_avatar_success(mock_file):
    """Test successful avatar upload."""
    with patch("cloudinary.uploader.upload") as mock_upload:
        mock_upload.return_value = {"secure_url": "https://example.com/avatar.jpg"}
        
        result = await upload_avatar(mock_file)
        assert result == "https://example.com/avatar.jpg"
        mock_upload.assert_called_once_with(
            mock_file.file,
            folder="avatars",
            resource_type="auto"
        )

@pytest.mark.asyncio
async def test_upload_avatar_invalid_file_type():
    """Test avatar upload with invalid file type."""
    invalid_file = MagicMock(spec=UploadFile)
    invalid_file.filename = "test.txt"
    invalid_file.content_type = "text/plain"
    invalid_file.file = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        await upload_avatar(invalid_file)
    
    assert exc_info.value.status_code == 500
    assert "Failed to upload avatar" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_upload_avatar_cloudinary_error(mock_file):
    """Test avatar upload with Cloudinary error."""
    with patch("cloudinary.uploader.upload") as mock_upload:
        mock_upload.side_effect = Exception("Cloudinary error")

        with pytest.raises(HTTPException) as exc_info:
            await upload_avatar(mock_file)
        
        assert exc_info.value.status_code == 500
        assert "Failed to upload avatar" in str(exc_info.value.detail) 