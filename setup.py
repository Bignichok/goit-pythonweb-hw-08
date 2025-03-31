import sys

from sqlalchemy import create_engine, text

from app.core.config import settings
from setup_db import setup_database


def check_postgres():
    """check if PostgreSQL is running and accessible"""
    try:
        # Try to connect to PostgreSQL
        engine = create_engine(settings.DATABASE_URL.rsplit("/", 1)[0])
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("PostgreSQL is running and accessible!")
        return True
    except Exception as e:
        print("\nPostgreSQL connection failed!")
        print("Please make sure:")
        print("1. PostgreSQL is installed")
        print("2. PostgreSQL service is running")
        print("3. Database credentials in .env file are correct")
        print(f"\nError: {str(e)}")
        return False


def main():
    print("Starting setup process...")

    # Check if PostgreSQL is running
    if not check_postgres():
        sys.exit(1)

    # Set up database and add sample data
    try:
        setup_database()
        print("\nSetup completed successfully!")
        print("\nYou can now run the application with:")
        print("poetry run uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\nSetup failed: {str(e)}")
        print("\nPlease make sure:")
        print("1. PostgreSQL is installed")
        print("2. PostgreSQL service is running")
        print("3. Database credentials in .env file are correct")
        sys.exit(1)


if __name__ == "__main__":
    main()
