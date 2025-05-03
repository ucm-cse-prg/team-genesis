"""
API Request and Response schemas Definitions based on Pydantic Models

These models are used to define the structure of data that is sent and received through the API.
"""

from app.models.student import Student as StudentModel
from beanie import PydanticObjectId
from typing import Optional
from pydantic import EmailStr
from app.models.skill import Skill


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

class updateStudentRequst(StudentModel):
    """
    Request schema for updating an existing student.
    """
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[EmailStr] = None,
    sid: Optional[str] = None,
    lab_section: Optional[str] = None,
    semester: Optional[str] = None,
    skills: Optional[list[Skill]] = None,
    preferences: Optional[dict[str, int]] = None,

class updateStudentResponse(StudentModel):
    """
    Response schema for updating an existing student.
    """
    id: PydanticObjectId