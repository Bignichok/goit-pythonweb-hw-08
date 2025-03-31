from sqlalchemy import Column, Date, Integer, String, Text

from app.core.database import Base


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    birthday = Column(Date, nullable=False)
    additional_data = Column(Text, nullable=True)
