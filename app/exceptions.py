"""
Custom exceptions for API error handling.

This file defines custom exceptions that should be used to provide graceful error handling,
logging, as well as meaningful HTTP responses with error messages to the client.
"""

import logging

from fastapi import status

logger = logging.getLogger("uvicorn.error")


class APIException(Exception):
    """
    Base exception class for API-related errors.

    This exception is raised when an API error occurs. It includes an HTTP status code
    and a descriptive error message.
    """

    def __init__(self, code: int, detail: str):
        # HTTP status code that indicates the type of error.
        self.code = code
        # A descriptive error message.
        self.detail = detail
        logger.warning(self.detail)

    def __str__(self) -> str:
        # Return the error message when the exception is printed.
        return self.detail


class InternalServerError(APIException):
    """
    Exception raised for internal server errors (HTTP 500).

    Inherits from APIException and automatically assigns a 500 HTTP status code.
    """

    def __init__(self, detail: str):
        # Initialize with HTTP 500 status code and a generic internal server error message.
        super().__init__(code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


# Implement custom exceptions to handle different types of API errors.
