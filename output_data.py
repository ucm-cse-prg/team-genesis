from typing import TypeAlias
from datatypes import Project

ProjectName: TypeAlias = str
AssignedPreferences: TypeAlias = dict[ProjectName, float]
ClasswidePreferences: TypeAlias = dict[ProjectName, float]


def write_to_file(projects: list[Project], filename: str):
    """
    Writes the project assignments to a file.

    Args:
        projects: A list of Project objects representing the project assignments.
        filename: The name of the file to write the assignments to.

    Returns:
        None
    """
    with open(filename, "w") as f:
        projects = sorted(projects, key=lambda project: project.team_number)
        for project in projects:
            f.write(
                f"{project.name} ({project.team_number}), Lab {project.assigned_lab}\n"
            )
            f.write(
                f"Skills: {', '.join([skill for skill in project.skills_dict if project.skills_dict[skill] == 1])}\n"
            )
            f.write("Student, Email - Relevant Skills\n")
            for student in project.assigned_students:
                f.write(f"{student.fn} {student.ln}, {student.email}")
                # for the sake of writing, uncapitalize the skills except for first letter
                f.write(
                    f" - {', '.join([skill[0]+skill[1:].lower() for skill in student.skills_ratings if student.skills_ratings[skill] > 5 and project.skills_dict[skill] == 1])}"
                )
                f.write(
                    f" - Preference for this project: {student.preferences[project.name]}\n"
                )
            f.write("\n")
