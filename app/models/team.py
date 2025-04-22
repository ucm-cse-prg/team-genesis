'''
Team Pydantic data model
'''

from typing import List
from pydantic import BaseModel, Field
from app.models.project import Project
from app.models.student import Student


class Team(BaseModel):
    lab_section: str = Field(
        title="Lab section",
        description="Lab section project was assigned to",
        min_length=3,
        max_length=3,
        examples=["02L","03L","04L"],
    )
    capacity: int = Field(
        title="Capacity",
        description="Capacity of team",
        gt=0,
    )
    assigned_project: Project = Field(
        title="Project",
        description="Project assigned to team",
    )
    members: List[Student] = Field(
        title="Members",
        description="The students working together on the assigned project",
    )
    skill_fulfillment_score: float = Field(
        title="Skill fulfillment score",
        description="A ratio of skills fulfilled over skills required"
    )
