from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from db import test_connection, Base, engine
import logging
import uvicorn

# Import routes
from routes import auth, users, transactions, redemptions, machines, rewards, vendo

# Setup logger
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    logger.info("Starting up VendoTrash application...")
    test_connection()
    
    # Create database tables
    logger.info("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully!")
        
        # Seed initial data
        from seed_db import seed_database
        seed_database()
    except Exception as e:
        logger.error(f"❌ Error initializing database: {str(e)}")
    
    yield
    # Shutdown (if needed in the future)
    logger.info("Shutting down application...")


app = FastAPI(
    title="VendoTrash API",
    description="VendoTrash Vending Machine API",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False  # Disable automatic trailing slash redirects
)

# CORS Middleware
# For local development: Allow all origins (ESP32-CAM needs this)
# For production: Restrict to specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for ESP32-CAM local network access
    # For production, replace with specific origins:
    # allow_origins=[
    #     "http://localhost:5175",
    #     "http://localhost:5173",
    #     "http://127.0.0.1:5175",
    #     "http://127.0.0.1:5173",
    #     "https://your-app.vercel.app",
    #     # Add Cloud Run URL when deployed
    # ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
app.include_router(redemptions.router, prefix="/api/redemptions", tags=["redemptions"])
app.include_router(machines.router, prefix="/api/machines", tags=["machines"])
app.include_router(rewards.router, prefix="/api/rewards", tags=["rewards"])
app.include_router(vendo.router, prefix="/api/vendo", tags=["vendo"])

# Debug: Log registered routes
logger.info("Registered routes:")
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        logger.info(f"  {list(route.methods)} {route.path}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to FastAPI Server"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/api/test-routes")
async def test_routes():
    """Test endpoint to verify routes are registered"""
    routes_info = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes_info.append({
                "path": route.path,
                "methods": list(route.methods)
            })
    return {"routes": routes_info, "total": len(routes_info)}


if __name__ == "__main__":
    """Run uvicorn server when main.py is executed directly"""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )

