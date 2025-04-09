"""
Database document models for Beanie ODM with MongoDB.
"""

from beanie import Document

# The DOCUMENTS list is used to register all document models with Beanie.
DOCUMENTS: list[
    Document
] = []  # List to hold all document models for Beanie initialization.


# Define Beanie document models that represent your MongoDB collections.
# Use Beanie's Document base class combined with Pydantic models
