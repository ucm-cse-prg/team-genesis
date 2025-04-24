"""
Actions for handling the internal logic of API endpoints.
"""

import typing
from functools import wraps
from importlib.metadata import metadata

from app.exceptions import InternalServerError

PROJECT_METADATA = metadata("fastapi-app")


# Wrapper function to run action and rais InternalServerError if it fails
@typing.no_type_check
def run_action(action):
    @wraps(action)
    async def wrapper(*args, **kwargs):
        try:
            # Call the wrapped function with provided arguments.
            return await action(*args, **kwargs)
        except Exception as e:
            # Convert APIException into HTTPException with corresponding code and message.
            raise InternalServerError(str(e))

    return wrapper


# Example usage of the run_action decorator
@run_action
async def home_page() -> str:
    # Get project metadata
    project_name = PROJECT_METADATA["Name"]
    project_version = PROJECT_METADATA["Version"]
    project_description = PROJECT_METADATA["Summary"]

    # Generate mockup HTML content for the home page
    content = f"""
        <html>
            <head>
                <title>{project_name}</title>
            </head>
            <body>
                <h1>Welcome to the {project_name}</h1>
                <p>{project_description}</p>
                <footer>
                    <p>version {project_version}</p>
                </footer>
            </body>
        </html>
        """

    # Uncomment the following line to raise an exception for testing purposes
    # raise Exception("This is a test exception")

    return content
