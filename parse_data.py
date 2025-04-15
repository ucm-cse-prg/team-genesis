import pandas as pd
from datatypes import Student, Project, LabName
import copy


def parse_data(
    student_project_data_file: str,
    skills_file: str,
) -> tuple[list[Student], list[Project]]:
    """Parses the student project data file and the skills file.
    The student project data file is an Excel file with multiple sheets. The
    skills file is a text file with one skill per line.
    The function returns a list of students and a list of projects.
    The student project data file is expected to have the following sheets:
    - MASTER: A sheet with the student data. The first row is the header row.
        The columns are Name, Email, LabSection, then skills.
    - Averages: A sheet with the average ratings for each project. The first row is
        the header row. The columns are the project names and the rows are the
        average ratings for each project.
    - PROJECTS: A sheet with the project data. The first row is the header row.
        The columns are Project Code, Project Name, and Skills. The rows are the
        project data.
    The skills file is expected to have one skill per line.

    Args:
        student_project_data_file (str): The path to the student project data file.
        skills_file (str): The path to the skills file.
    Returns:
        tuple[list[Student], list[Project]]: A tuple containing a list of students and
            a list of projects.
    """
    student_df = pd.read_excel(
        student_project_data_file,
        sheet_name="MASTER",
        index_col=None,
    )

    lab_populations: dict[LabName, int] = {}
    for i in range(len(student_df)):
        lab = student_df.at[i, "Lab"]
        if pd.isna(lab):
            break
        lab_populations[lab] = lab_populations.get(lab, 0) + 1

    with open(skills_file, "r") as f:
        SKILLS = f.read().splitlines()

    project_df = pd.read_excel(
        student_project_data_file,
        sheet_name="Averages",
        index_col="index",
    )
    project_df_2 = pd.read_excel(
        student_project_data_file,
        sheet_name="PROJECTS",
        index_col="Project Code",
    )

    projects: list[Project] = []

    for name in project_df.columns[:-4]:
        # Determine correct key for team and skills
        key = name if name in project_df_2.index else f"{name}1"

        team_number = project_df_2.at[key, "Team #"]
        skills_list: list[str] = project_df_2.at[key, "Skills"].split(", ")

        skills_dict: dict[str, int] = {
            skill.upper(): 1 if skill.upper() in map(str.upper, skills_list) else 0
            for skill in SKILLS
        }

        projects.append(Project(name, team_number, skills_dict))


    students: list[Student] = []
    # last row is nan, first row is headers
    for i in range(len(student_df)):
        s = Student(student_df, projects, i, SKILLS)

        students.append(s)

    # columns are Name, Email, LabSection, then skills
    student_df_2 = pd.read_excel(
        student_project_data_file,
        sheet_name="survey_results3",
        index_col=None,
    )
    for i in range(len(student_df_2)):
        student = students[i]
        for skill in SKILLS:
            student.skills_ratings[skill] = int(float(student_df_2.at[i, skill]) * 2)

    to_duplicate: list[str] = [
        "X10eML",
        "X10eLLM",
        "SOE",
        "SEM",
        "WD",
        "MSt",
        "UNi",
        "BART",
        "AGR",
        "HIL",
        "I2Gs",
        "I2Gn",
        "MSp",
        "SW",
        "OWL",
    ]
    for project in projects:
        if project.name in to_duplicate:
            for student in students:
                student.preferences[f"{project.name}1"] = student.preferences[
                    project.name
                ]
                student.preferences[f"{project.name}2"] = student.preferences[
                    project.name
                ]
                del student.preferences[project.name]

            projects.append(copy.deepcopy(project))
            project.name = f"{project.name}1"
            projects[-1].name = f"{projects[-1].name}2"

    return students, projects
