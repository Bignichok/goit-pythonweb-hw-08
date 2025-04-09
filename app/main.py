import logging

import redis.asyncio as redis
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from app.api import auth, contacts
from app.core.config import settings
from app.core.database import Base, engine, init_db

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


# Initialize rate limiter and database
@app.on_event("startup")
async def startup():
    try:
        # Initialize Redis rate limiter
        r = redis.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
            password=settings.REDIS_PASSWORD,
            encoding="utf-8",
            decode_responses=True,
        )
        await FastAPILimiter.init(r)
        logging.info("Redis rate limiter initialized successfully")
    except Exception as e:
        logging.warning(f"Failed to initialize Redis rate limiter: {e}")
        # If Redis is not available, we'll skip rate limiting
        app.dependency_overrides[RateLimiter] = lambda: None

    # Initialize database
    await init_db()
    logging.info("Database initialized successfully")


# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])

# Contacts router with optional rate limiting
app.include_router(
    contacts.router,
    prefix=f"{settings.API_V1_STR}/contacts",
    tags=["contacts"],
    dependencies=(
        [Depends(RateLimiter(times=10, seconds=60))]
        if hasattr(app, "dependency_overrides")
        and RateLimiter in app.dependency_overrides
        else []
    ),
)


@app.get("/")
def read_root():
    return {"message": "Welcome to Contact API"}
