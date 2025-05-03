"""
API endpoints for the application.
"""

import typing
from functools import wraps

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from app.schemas import createStudentRequst, createStudentResponse
import app.documents as Documents
import app.actions as Actions
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

@router.post("/students", response_model=createStudentResponse, status_code=201)
@http_exception
async def create_student(
    student: createStudentRequst,
) -> Documents.Student:
    try:
        return await Actions.create_student(**student.model_dump())
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=e.detail)

@router.delete("/students/{id}", status_code=204)
@http_exception
async def delete_student(student: Documents.Student) -> None:
    try:
        await Actions.delete_student(student)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=e.detail)