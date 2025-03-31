from datetime import date

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base
from app.models.contact import Contact


def setup_database():
    # Create engine without database name
    engine = create_engine(settings.DATABASE_URL.rsplit("/", 1)[0])

    # Create database if it doesn't exist
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))  # Close any open transactions
        conn.execute(text(f"CREATE DATABASE contacts_db"))

    # Create engine with database name
    engine = create_engine(settings.DATABASE_URL)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    # Add sample data
    sample_contacts = [
        Contact(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="+1234567890",
            birthday=date(1990, 1, 1),
            additional_data="Sample contact 1",
        ),
        Contact(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            phone="+0987654321",
            birthday=date(1995, 5, 15),
            additional_data="Sample contact 2",
        ),
        Contact(
            first_name="Bob",
            last_name="Johnson",
            email="bob.johnson@example.com",
            phone="+1122334455",
            birthday=date(1985, 12, 25),
            additional_data="Sample contact 3",
        ),
    ]

    # Add contacts to database
    for contact in sample_contacts:
        db.add(contact)

    # Commit changes
    db.commit()

    print("Database setup completed successfully!")
    print("Sample contacts have been added to the database.")


if __name__ == "__main__":
    setup_database()
