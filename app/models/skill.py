'''
Skill pydantic data model
'''

from pydantic import BaseModel, Field

class Skill(BaseModel):
    name: str = Field(
        title="Skill name",
        description="Name of the skill",
        min_length=3,
        max_length=50,
        examples=["Python", "Java", "C++"],
    )
    proficiency_level: int = Field(
        title="Proficiency level",
        description="Proficiency level of the skill (1-5)",
        gt=0,
        le=5,
    )