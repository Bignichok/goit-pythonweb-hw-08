import pytest
from unittest.mock import patch
import os
from pydantic import ValidationError

from app.core.config import Settings

@pytest.fixture
def mock_env_vars():
    env_vars = {
        'DATABASE_URL': 'postgresql://user:pass@localhost:5432/test_db',
        'SECRET_KEY': 'test_secret_key',
        'ALGORITHM': 'HS256',
        'ACCESS_TOKEN_EXPIRE_MINUTES': '30',
        'REFRESH_TOKEN_EXPIRE_DAYS': '7',
        'SMTP_SERVER': 'smtp.example.com',
        'SMTP_PORT': '587',
        'SMTP_USERNAME': 'test@example.com',
        'SMTP_PASSWORD': 'test_password',
        'REDIS_HOST': 'localhost',
        'REDIS_PORT': '6379',
        'CLOUDINARY_CLOUD_NAME': 'test_cloud',
        'CLOUDINARY_API_KEY': 'test_api_key',
        'CLOUDINARY_API_SECRET': 'test_api_secret'
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars

def test_settings_default_values():
    """Test settings with default values."""
    settings = Settings()
    assert settings.DATABASE_URL is not None
    assert settings.SECRET_KEY is not None
    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 7
    assert settings.SMTP_PORT == 587
    assert settings.REDIS_PORT == 6379

def test_settings_env_vars(mock_env_vars):
    settings = Settings()
    assert settings.DATABASE_URL == mock_env_vars['DATABASE_URL']
    assert settings.SECRET_KEY == mock_env_vars['SECRET_KEY']
    assert settings.ALGORITHM == mock_env_vars['ALGORITHM']
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == int(mock_env_vars['ACCESS_TOKEN_EXPIRE_MINUTES'])
    assert settings.REFRESH_TOKEN_EXPIRE_DAYS == int(mock_env_vars['REFRESH_TOKEN_EXPIRE_DAYS'])
    assert settings.SMTP_SERVER == mock_env_vars['SMTP_SERVER']
    assert settings.SMTP_PORT == int(mock_env_vars['SMTP_PORT'])
    assert settings.SMTP_USERNAME == mock_env_vars['SMTP_USERNAME']
    assert settings.SMTP_PASSWORD == mock_env_vars['SMTP_PASSWORD']
    assert settings.REDIS_HOST == mock_env_vars['REDIS_HOST']
    assert settings.REDIS_PORT == int(mock_env_vars['REDIS_PORT'])
    assert settings.CLOUDINARY_CLOUD_NAME == mock_env_vars['CLOUDINARY_CLOUD_NAME']
    assert settings.CLOUDINARY_API_KEY == mock_env_vars['CLOUDINARY_API_KEY']
    assert settings.CLOUDINARY_API_SECRET == mock_env_vars['CLOUDINARY_API_SECRET']

def test_settings_invalid_env_vars():
    """Test settings with invalid environment variables."""
    with patch.dict(os.environ, {
        'ACCESS_TOKEN_EXPIRE_MINUTES': 'invalid',
        'REFRESH_TOKEN_EXPIRE_DAYS': 'invalid',
        'SMTP_PORT': 'invalid',
        'REDIS_PORT': 'invalid'
    }):
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        
        errors = exc_info.value.errors()
        assert len(errors) == 4
        
        # Check each field's error
        for error in errors:
            assert error['type'] == 'int_parsing'
            assert 'Input should be a valid integer' in error['msg']
            assert error['input'] == 'invalid'
            
        # Verify all expected fields are in the errors
        error_fields = {error['loc'][0] for error in errors}
        assert error_fields == {
            'ACCESS_TOKEN_EXPIRE_MINUTES',
            'REFRESH_TOKEN_EXPIRE_DAYS',
            'SMTP_PORT',
            'REDIS_PORT'
        } 