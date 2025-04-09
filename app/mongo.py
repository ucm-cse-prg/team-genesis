"""
Module for initializing MongoDB connection and configuring Beanie ODM.

This module sets up the connection to the MongoDB database using Motor and initializes
Beanie with the application's document models.
"""

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import get_settings
from app.documents import DOCUMENTS

# Retrieve application settings which include MongoDB connection details.
SETTINGS = get_settings()


async def init_mongo() -> None:
    """
    Initialize the MongoDB connection and configure Beanie ODM.

    This function creates a Motor client using the MongoDB URL from the settings,
    selects the database specified in settings, and initializes Beanie with the document
    models. It should be called during application startup.

    Raises:
        Exception: If unable to connect to MongoDB or initialize Beanie.
    """

    # Create a Motor client to interact with MongoDB.
    client: AsyncIOMotorClient = AsyncIOMotorClient(SETTINGS.mongodb_url)

    # Access the database using the name provided in the settings.
    db = client[SETTINGS.db_name]

    # Initialize Beanie with the database and the list of document models.
    await init_beanie(database=db, document_models=DOCUMENTS)


async def drop_database() -> None:
    """
    Drop the database specified in the application settings.

    This function is used for testing purposes to drop the database before running tests.
    It should not be used in a production environment.

    Raises:
        Exception: If unable to drop the database.
    """
    client: AsyncIOMotorClient = AsyncIOMotorClient(SETTINGS.mongodb_url)
    await client.drop_database(SETTINGS.db_name)


async def close_mongo() -> None:
    """
    Close the MongoDB connection.

    This function closes the MongoDB connection when the application is shutting down.
    """
    client: AsyncIOMotorClient = AsyncIOMotorClient(SETTINGS.mongodb_url)
    client.close()
