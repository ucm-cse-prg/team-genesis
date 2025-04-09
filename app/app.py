"""
This is the main application file for the FastAPI application.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.api import router
from app.config import get_settings
from app.mongo import close_mongo, init_mongo

# Load application settings from environment or configuration.
SETTINGS = get_settings()


# Function to run on application startup.
async def startup() -> None:
    """
    Startup function to initialize the application.

    This function is called when the FastAPI application starts up.
    It initializes the MongoDB connection and sets up Beanie ODM.
    """
    await init_mongo()
    # Additional startup logic can be added here.


# Function run on application shutdown.
async def shutdown() -> None:
    """
    Shutdown function to clean up resources.

    This function is called when the FastAPI application shuts down.
    It closes the MongoDB connection and performs any necessary cleanup.
    """
    await close_mongo()
    # Additional shutdown logic can be added here.


# Lifespan context manager for FastAPI application.
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan context manager for FastAPI.

    This context manager handles startup and shutdown events for the application.
    On startup, it connects to MongoDB by calling init_mongo().
    On shutdown, any required cleanup logic (e.g., closing database connections)
    can be added here.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None: Control is yielded back after startup actions.
    """
    await startup()  # Connect to MongoDB during app startup
    yield  # Yield control back to the application
    await shutdown()  # Perform cleanup actions on app shutdown


# Create a FastAPI application instance, using the custom lifespan context manager.
app = FastAPI(lifespan=lifespan)

# Include API routes
app.include_router(router)
