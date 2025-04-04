from app.core.database import init_db
from app.models.contact import Contact
from app.models.user import User

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
