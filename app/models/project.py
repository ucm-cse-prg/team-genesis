"""
Project Pydantic data model
"""

from typing import Dict, Optional
from pydantic import BaseModel, Field
from app.models.skill import Skill

class Project(BaseModel):
    name: str = Field(
        title="Name",
        description="Name of project",
        pattern=r"^[A-Za-z0-9,'\"]+$",
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
    required_skills: list[Skill] = Field(
        title="Required skills",
        description="A list of skills that a project needs to complete",
        default=None
    )
