"""
Data Models based on Pydantic Models

These Models form the backbone of the application, providing a way to validate and serialize data.
Request/response schemas as well as database documents are derived from these models.
"""

from __future__ import annotations
from typing import dict, List, Optional
from pydantic import BaseModel, Field, EmailStr 


class Student(BaseModel):
    first_name: str = Field(
        title="First name",
        description="First name of the student",
    )
    last_name: str = Field(
        title="Last name",
        description="Last name of the student",
    )
    email: EmailStr = Field(
        title="Email",
        description="Email of the student",
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
    skills: Optional[dict[str, float]] = Field(
        title="Skills dictionary",
        description="A dictionary of skills that the student self rates. Keys are skills and values are a float",
        default = None,
    )
    preferences: Optional[dict[str, int]] = Field(
        title="Student project preferences",
        description="A dictionary containing the student's project preferences. Keys are projects and values are ints.",
        default=None,
    )
    match_score: Optional[float] = Field(
        title="Match Score",
        description="The match score between a student and their assigned Project",
        default=None,
    )
    assigned_project: Optional["Project"] = Field(
        title="Assigned project",
        description="The Project assigned to the student",
        default=None,
    )


class Project(BaseModel):
    name: str = Field(
        title="Name",
        description="Name of project",

    )
    description: str = Field(
        title="Description",
        description="Description of project",

    )
    semester: str = Field(
        title="Semester",
        description="Semester project is offered",
        min_length=8,
        max_length=10,
        examples=["Fall2024", "Spring2025"],
    )
    lab_section: Optional[str] = Field(
        title="Lab section",
        description="Lab section project has been assigned to",
        min_length=3,
        max_length=3, 
        default=None,
    )
    required_skills: Optional[dict[str, float]]  = Field(
        title="Required skills",
        description="A list of skills that a project needs to complete",
        default=None    
    )
    max_team_size: Optional[int] = Field(
        title="Maximum team size",
        description="The maximum number of Students a project can have in its team",
        default=None
    )
    team: Optional[List[Student]] = Field(
        title="Team",
        description="All of the students assigned to this project",
        default_factory=list,
    )
    total_match_score: Optional[float] = Field(
        title="Total match score",
        description="A sum of all of the match scores of the students in the team",
        default=None,
    )
    skill_fullfillment_score: Optional[float] = Field(
        title="Skill fulfillment score",
        description="A ratio of number skills fulfilled over number of skills required",
        default=None,
    )


# to resolve the circular dependency between students and projects
Student.model_rebuild()
Project.model_rebuild()