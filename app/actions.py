"""
Actions for handling the internal logic of API endpoints.
"""

import typing
from functools import wraps
from importlib.metadata import metadata
from pydantic import EmailStr
from typing import Optional
from app.exceptions import InternalServerError
from app.documents import Student
from app.models.skill import Skill

PROJECT_METADATA = metadata("team-genesis")


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

async def create_student(
    first_name: str,
    last_name: str,
    email: EmailStr,
    sid: str,
    lab_section: str,
    semester: str,
    skills: list[Skill],
    preferences: typing.Optional[dict[str, int]] = None,
) -> Student:
    new_student: Student = await Student(
        first_name=first_name,
        last_name=last_name,
        email=email,
        sid=sid,
        lab_section=lab_section,
        semester=semester,
        skills=skills,
        preferences=preferences,
    ).insert()

    if not new_student:
        raise InternalServerError("Failed to create student")
    
    return new_student

async def delete_student(student: Student) -> None:
    await Student.delete(student)

    if await Student.get(student.id):
        raise InternalServerError("Failed to delete student")

async def update_student(
    student: Student,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[EmailStr] = None,
    sid: Optional[str] = None,
    lab_section: Optional[str] = None,
    semester: Optional[str] = None,
    skills: Optional[list[Skill]] = None,
    preferences: Optional[dict[str, int]] = None,
) -> Student:
    if first_name is not None:
        student.first_name = first_name
    if last_name is not None:
        student.last_name = last_name
    if email is not None:
        student.email = email
    if sid is not None:
        student.sid = sid
    if lab_section is not None:
        student.lab_section = lab_section
    if semester is not None:
        student.semester = semester
    if skills is not None:
        student.skills = skills
    if preferences is not None:
        student.preferences = preferences

    updated_student = await student.update()

    if not updated_student:
        raise InternalServerError("Failed to update student")

    return updated_student
