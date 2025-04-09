from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
metadata = MetaData()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Import models to ensure they are registered with Base.metadata
    from app.models.user import User
    from app.models.contact import Contact
    
    # Drop tables in reverse order of dependencies
    metadata.reflect(bind=engine)
    if 'contacts' in metadata.tables:
        metadata.tables['contacts'].drop(engine)
    if 'users' in metadata.tables:
        metadata.tables['users'].drop(engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
