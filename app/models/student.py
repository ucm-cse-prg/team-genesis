'''
Student Pydantic data model
'''

from typing import Dict, Optional
from pydantic import BaseModel, Field, EmailStr 
from app.models.skill import Skill

class Student(BaseModel):
    first_name: str = Field(
        title="First name",
        description="First name of the student",
        pattern=r"^[A-Za-z]+$",
    )
    last_name: str = Field(
        title="Last name",
        description="Last name of the student",
        pattern=r"^[A-Za-z]+$",
    )
    email: EmailStr = Field(
        title="Email",
        description="Email of the student",
    )
    sid: str = Field(
        title="Student ID",
        description="Student ID of the student",
        pattern=r"^[0-9]{9}$",
    )
    lab_section: str = Field(
        title="Lab section",
        description="Lab section student registered for",
        min_length=3,
        max_length=3, 
        examples=["02L","03L","04L"],
    )
    semester: str = Field(
        title="Semester",
        description="Semester student is taking capstone",
        min_length=8,
        max_length=10,
        examples=["Fall2024", "Spring2025"],
    )
    skills: list[Skill] = Field(
        title="Skills list",
        description="A list of skills that the student self rates. Keys are skills and values are a float",
        default = None,
    )
    preferences: Optional[Dict[str, int]] = Field(
        title="Student project preferences",
        description="A dictionary containing the student's project preferences. Keys are projects and values are ints.",
        default=None,
    )