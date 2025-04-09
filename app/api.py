"""
API endpoints for the application.
"""

import typing
from functools import wraps

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from app.actions import home_page
from app.exceptions import APIException

router = APIRouter()


# This decorator is used to handle exceptions that occur in the API endpoints.
@typing.no_type_check
def http_exception(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # Try to make the API call and return the result if successful.
            return await func(*args, **kwargs)
        except APIException as e:
            # If an exception occurs, raise an HTTPException with the error code and detail.
            raise HTTPException(status_code=e.code, detail=e.detail)

    return wrapper


@router.get("/")
@http_exception
async def root() -> HTMLResponse:
    content: str = await home_page()
    return HTMLResponse(
        content=content,
        status_code=200,
    )
