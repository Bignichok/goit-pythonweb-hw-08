from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import contacts
from app.core.config import settings
from app.core.database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    contacts.router, prefix=f"{settings.API_V1_STR}/contacts", tags=["contacts"]
)


@app.get("/")
def read_root():
    return {"message": "Welcome to Contact API"}
