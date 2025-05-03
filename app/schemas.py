"""
API Request and Response schemas Definitions based on Pydantic Models

These models are used to define the structure of data that is sent and received through the API.
"""

from app.models.student import Student as StudentModel
from beanie import PydanticObjectId


class createStudentRequst(StudentModel):
    """
    Request schema for creating a new student.
    """
    pass

class createStudentResponse(StudentModel):
    """
    Response schema for creating a new student.
    """
    id: PydanticObjectId