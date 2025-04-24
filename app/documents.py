"""
Database document models for Beanie ODM with MongoDB.
"""

from .models import Student as StudentModel
from .models import Project as ProjectModel
from .models import Team as TeamModel
from beanie import Document


class Student(Document, StudentModel):
    class Settings:
        name= "Students"

class Project(Document, ProjectModel):
    class Settings:
        name= "Projects"

class Team(Document, TeamModel):
    class Settings:
        name= "Teams"


# The DOCUMENTS list is used to register all document models with Beanie.
DOCUMENTS: list[
    Document
] = [Student, Project, Team] # type: ignore
