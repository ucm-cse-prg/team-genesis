"""Fixtures module for testing.

This module contains pytest fixtures used to configure the event loop
and provide an asynchronous HTTP client for testing the ASGI application.
"""

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from app.app import app


@pytest.fixture()
async def client_test():
    """
    Create and yield an asynchronous HTTP client for testing the ASGI app.

    This fixture uses LifespanManager to handle the startup and shutdown events
    of the app and configures an AsyncClient with ASGITransport to interact with the app.

    Yields:
        AsyncClient: An HTTP client instance configured for testing API endpoints.
    """
    # Ensure the app's lifespan events (startup and shutdown) are managed properly.
    async with LifespanManager(app):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            follow_redirects=True,
        ) as ac:
            yield ac
