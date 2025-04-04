# Contact Management API

A RESTful API for managing contacts with authentication, rate limiting, and email verification built using FastAPI and SQLAlchemy.

## Features

- User authentication with JWT tokens
- Email verification (optional in development)
- Rate limiting (optional in development)
- Contact management (CRUD operations)
- Birthday notifications
- Avatar upload with Cloudinary
- PostgreSQL database
- Redis for rate limiting (optional in development)
- CORS support

## Prerequisites

- Python 3.12+
- PostgreSQL
- Redis (optional for development)
- Cloudinary account
- SMTP server (optional for development)
- Poetry for dependency management

## Quick Start for Development

1. Clone the repository:
```bash
git clone <repository-url>
cd contact-api
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Create a `.env` file in the root directory:
```env
# Database (Required)
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/contacts_db

# JWT Authentication (Required)
SECRET_KEY=your-secret-key-here  # A secure random string
ALGORITHM=HS256  # Default: HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30  # Default: 30
REFRESH_TOKEN_EXPIRE_DAYS=7  # Default: 7

# Email Settings (Optional for development)
SMTP_USER=""  # Can be empty in development
SMTP_PASSWORD=""  # Can be empty in development
SMTP_HOST=localhost
SMTP_PORT=1025

# Cloudinary (Optional until you need avatar uploads)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Redis (Optional for development)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=""  # Can be empty in development
```

4. Initialize the database:
```bash
poetry run python init_db.py
```

5. Start the server:
```bash
poetry run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Authentication

### Register a New User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
           "email": "user@example.com",
           "password": "password123"
         }'
```

Response:
```json
{
  "id": 1,
  "email": "user@example.com",
  "is_active": true,
  "is_verified": true,
  "avatar": null,
  "created_at": "2024-02-14T12:00:00"
}
```

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=user@example.com&password=password123"
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV...",
  "refresh_token": "eyJ0eXAiOiJKV...",
  "token_type": "bearer"
}
```

### Using Authentication

For all protected endpoints, include the access token in the Authorization header:
```bash
curl -H "Authorization: Bearer your_access_token" ...
```

## Development Features

### Email Verification
- In development, email verification is optional
- Users are automatically verified upon registration
- If you want to test email functionality:
  ```bash
  # In a separate terminal, run a local SMTP server
  python -m smtpd -c DebuggingServer -n localhost:1025
  ```

### Rate Limiting
- In development, rate limiting is optional
- If Redis is not available, the API will work without rate limits
- For production, ensure Redis is properly configured

## Contacts API

### Create Contact
```bash
curl -X POST "http://localhost:8000/api/v1/contacts" \
     -H "Authorization: Bearer your_access_token" \
     -H "Content-Type: application/json" \
     -d '{
           "first_name": "John",
           "last_name": "Doe",
           "email": "john@example.com",
           "phone": "+1234567890",
           "birthday": "1990-01-01"
         }'
```

### Get All Contacts
```bash
curl -X GET "http://localhost:8000/api/v1/contacts" \
     -H "Authorization: Bearer your_access_token"
```

### Search Contacts
```bash
curl -X GET "http://localhost:8000/api/v1/contacts?search=John" \
     -H "Authorization: Bearer your_access_token"
```

### Get Contact by ID
```bash
curl -X GET "http://localhost:8000/api/v1/contacts/1" \
     -H "Authorization: Bearer your_access_token"
```

### Update Contact
```bash
curl -X PUT "http://localhost:8000/api/v1/contacts/1" \
     -H "Authorization: Bearer your_access_token" \
     -H "Content-Type: application/json" \
     -d '{
           "first_name": "John",
           "last_name": "Smith"
         }'
```

### Delete Contact
```bash
curl -X DELETE "http://localhost:8000/api/v1/contacts/1" \
     -H "Authorization: Bearer your_access_token"
```

### Get Upcoming Birthdays
```bash
curl -X GET "http://localhost:8000/api/v1/contacts/birthdays/upcoming" \
     -H "Authorization: Bearer your_access_token"
```

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- 400: Bad Request - Invalid input
- 401: Unauthorized - Invalid or missing authentication
- 403: Forbidden - Insufficient permissions
- 404: Not Found - Resource not found
- 409: Conflict - Resource already exists
- 429: Too Many Requests - Rate limit exceeded
- 500: Internal Server Error - Server error

## Development

### Running Tests
```bash
poetry run pytest
```

### Code Formatting
```bash
poetry run black .
poetry run isort .
```

### Linting
```bash
poetry run flake8
```

## Production Deployment

For production deployment, ensure:

1. Redis is properly configured for rate limiting
2. SMTP server is configured for email verification
3. Cloudinary is configured for avatar uploads
4. PostgreSQL is secured and properly configured
5. Strong SECRET_KEY is set
6. CORS origins are properly restricted
7. Debug mode is disabled

## License

This project is licensed under the MIT License - see the LICENSE file for details. 