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
SMTP_SERVER=smtp.gmail.com  # Default: smtp.gmail.com
SMTP_PORT=587  # Default: 587
SMTP_USERNAME=your-email@gmail.com  # Required
SMTP_PASSWORD=your-app-password  # Required

# Cloudinary (Optional until you need avatar uploads)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Redis (Optional for development)
REDIS_HOST=localhost  # Default: localhost
REDIS_PORT=6379  # Default: 6379
REDIS_PASSWORD=""  # Optional
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

## Testing

The project includes unit tests and integration tests. To run the tests:

1. Make sure you have all dependencies installed:
```bash
poetry install
```

2. Run unit tests:
```bash
poetry run pytest tests/unit
```

3. Run integration tests:
```bash
poetry run pytest tests/integration
```

4. Run tests with coverage report:
```bash
poetry run pytest --cov=app --cov-report=term-missing
```

5. Run specific test file:
```bash
poetry run pytest tests/unit/test_auth.py
```

6. Run tests with verbose output:
```bash
poetry run pytest -v
```

7. Run tests and stop on first failure:
```bash
poetry run pytest -x
```

The test suite includes:
- Authentication tests (JWT, password hashing, user verification)
- Email service tests (verification and password reset emails)
- Database operation tests
- Contact management tests
- Rate limiting tests
- Cloudinary integration tests

Note: Tests use a separate test database and mock external services (SMTP, Cloudinary, Redis) to ensure reliable and isolated testing.

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

The project uses Sphinx for comprehensive API documentation. The documentation is available in two formats:

1. Interactive API Documentation (Auto-generated by FastAPI):
   - Swagger UI: `http://localhost:8000/api/v1/docs`
   - ReDoc: `http://localhost:8000/api/v1/redoc`

2. Sphinx Documentation:
   - Source files are located in `docs/source/`
   - Built documentation is available in `docs/build/html/`

### Building Documentation

To build the Sphinx documentation:

1. Install Sphinx and dependencies:
```bash
poetry install
```

2. Build the HTML documentation:
```bash
cd docs
poetry run make html
```

The built documentation will be available in `docs/build/html/`. Open `index.html` in your browser to view it.

### Documentation Structure

The Sphinx documentation is organized into the following sections:

- **Authentication**: Documentation for authentication endpoints and schemas
- **Contacts**: Documentation for contact management endpoints and models
- **Models**: Detailed documentation of database models
- **Schemas**: Documentation of Pydantic schemas used for request/response validation

Each module is documented using docstrings following the Google style format.

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