from sqlalchemy import MetaData, create_engine, inspect
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a new metadata object
metadata = MetaData()

# Create the declarative base
Base = declarative_base(metadata=metadata)


def init_db():
    # Get database inspector
    inspector = inspect(engine)

    # Drop all existing tables
    for table_name in inspector.get_table_names():
        metadata.drop_all(bind=engine, tables=[metadata.tables[table_name]])

    # Create all tables
    metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
