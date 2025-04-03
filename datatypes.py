import re
import pandas as pd

class Project:
    """A project that students will be assigned to.

    Attributes:
        name (str): The unique name of the project.
        original_name (str): The name of the project without the duplication tag ("_1"
            or "_2").
        assigned_lab (str): The lab that the project is assigned to (02L, 03L, etc.).
        assigned_students (list[Student]): A list of students assigned to the
            project.
        team_capacity (int): The number of students that can be assigned to the project.
        skills_dict (dict[str, int]): A dictionary mapping skills to 1 if the skill is
            required for the project and 0 otherwise. Contains all possible skills
            across all projects as keys.
    """

    def __init__(self, name: str, skills: list[str]) -> None:
        """Initializes the instance based on the name and possible skills.

        original_name is initialized as described in the class docstring. All other
        attributes are initialized to dummy values.

        Args:
            name (str): The unique name of the project.
            skills (list[str]): A list of possible skills for the project, all values
                initalized to zero.
        Returns:
            None
        """
        self.name = name
        self.original_name = name.split("_")[0]
        self.assigned_lab = ""
        self.assigned_students: list[Student] = []
        self.team_capacity = 0

        self.skills_dict = {key: 0 for key in skills}


class Student:
    """A student that will be assigned to a project.

    Attributes:
        assigned_project (str): The name of the project that the student is assigned to.
        fn (str): The first name of the student.
        ln (str): The last name of the student.
        email (str): The email of the student.
        lab (str): The lab that the student is assigned to (02L, 03L, etc.).
        skills_ratings (dict[str, int]): A dictionary mapping skills to the student's
            rating for that skill.
        preferences (dict[str, int]): A dictionary mapping project names to the
            preference score of the student for that project.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        projects: list[Project],
        i: int,
        skills: list[str],
    ) -> None:
        """Initializes the instance based on the dataframe and project list.

        All attributes are scraped based on the student dataframe and a given index.

        Args:
            df: The dataframe containing the student data. It should contain the headers
                "First Name", "Last Name", "Email", "Lab", "Skills", "Proficient", and
                the project names (containing preference ratings) The rows should be
                student data.
            projects: A list of Project objects to assign to labs.
            i: The index of the student in the dataframe.
            skills: A list of possible skills for the project.
        Returns:
            None
        """
        self.assigned_project = ""

        self.fn = df.at[i, "First Name"]
        self.ln = df.at[i, "Last Name"]
        self.email = df.at[i, "Email"]
        self.lab = df.at[i, "Lab"]

        scraped_skills = (
            re.sub(r"\([^)]*\)", "", df.at[i, "Skills"])
            .upper()
            .split(",")
        )
        proficiencies = (
            re.sub(r"\([^)]*\)", "", str(df.at[i, "Proficient"]))
            .upper()
        )
        parsed_proficient_skills = []
        self.skills_ratings = {key: 0 for key in skills}
        for skill in scraped_skills:
            skill=skill.strip()
            if skill == "WEB DEVELOPMENT":
                skill = "WEB DEV"
            if skill == "MACHINE LEARNING":
                skill = "ML"
            if skill == "APP DEVELOPMENT":
                skill = "APP DEV"
            if "DATABASES" in skill:
                skill = "DATA MANAGEMENT"
            if skill in self.skills_ratings:
                self.skills_ratings[skill] = 3
                if skill in proficiencies:
                    parsed_proficient_skills.append(skill)
        if len(parsed_proficient_skills) <= 5:
            for skill in parsed_proficient_skills:
                self.skills_ratings[skill] = 8

        self.preferences: dict[str, int] = {}
        for project in projects:
            self.preferences[project.name] = df.at[i, project.original_name]