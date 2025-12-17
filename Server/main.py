from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from db import test_connection
import logging
import uvicorn

# Import routes
from routes import auth, users, bookings

# Setup logger
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    logger.info("Starting up application...")
    test_connection()
    yield
    # Shutdown (if needed in the future)
    logger.info("Shutting down application...")


app = FastAPI(
    title="FastAPI Server",
    description="A simple FastAPI template",
    version="1.0.0",
    lifespan=lifespan
)

# Register routes
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(bookings.router, prefix="/bookings", tags=["bookings"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to FastAPI Server"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    """Run uvicorn server when main.py is executed directly"""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )

