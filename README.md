# Contact Management API

A REST API for managing contacts built with FastAPI and SQLAlchemy.

## Features

- CRUD operations for contacts
- Search contacts by name, surname, or email
- Birthday notifications for upcoming 7 days
- PostgreSQL database integration
- Swagger documentation
- Pydantic validation
- CORS middleware

## Prerequisites

- Python 3.12+
- PostgreSQL
- Poetry for dependency management

## Installation

1. Clone the repository

2. Install dependencies:
```bash
poetry install
```

3. Create a `.env` file in the root directory with the following content:
```
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/contacts_db
```
Replace `your_password` with the password you set during PostgreSQL installation.

4. Make sure PostgreSQL is running:
   - Open Windows Services (services.msc)
   - Find "PostgreSQL" service
   - Make sure it's running (Status should be "Running")
   - If not running, right-click and select "Start"

5. Run the setup script to create the database and add sample data:
```bash
poetry run python setup.py
```

6. Run the application:
```bash
poetry run uvicorn app.main:app --reload
```

## API Documentation

Once the application is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

- `POST /api/v1/contacts/` - Create a new contact
- `GET /api/v1/contacts/` - List all contacts (with search)
- `GET /api/v1/contacts/{contact_id}` - Get a specific contact
- `PUT /api/v1/contacts/{contact_id}` - Update a contact
- `DELETE /api/v1/contacts/{contact_id}` - Delete a contact
- `GET /api/v1/contacts/birthdays/upcoming` - Get contacts with birthdays in the next 7 days

## Project Structure

```
contact-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── contact.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── contact.py
│   └── api/
│       ├── __init__.py
│       └── contacts.py
├── tests/
│   └── __init__.py
├── .env
├── .gitignore
├── pyproject.toml
├── setup.py
├── setup_db.py
└── README.md
```

## Troubleshooting

If you encounter any issues:

1. Make sure PostgreSQL is installed and running
2. Check your database credentials in the `.env` file
3. Verify that the PostgreSQL service is running
4. Check the error messages in the setup script output

## Development

To run tests:
```bash
poetry run pytest
```

To format code:
```bash
poetry run black .
poetry run isort .
``` 