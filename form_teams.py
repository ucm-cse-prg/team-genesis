from pprint import pprint
import pandas as pd
import numpy as np
from collections import defaultdict
import copy
import re

# our version doesn't ship with typehints
import pymongo  # type: ignore
import matplotlib.pyplot as plt
from typing import Optional, TypeAlias, Any
import json

import random

""" notes/WIP
multiaxis:
x is projects,
y1 is avg pref score of students in projects,
y2 is % of fulfilled skills in project

stretch goal: rotate student lists like lab assignments
THIS DOES NOTHING ^^^^^^^^

- add average preference for proj across all students to bar plot
- cross validate on preference scalar -> WHAT SCORE TO MAXIMIZE
- add skill score attr ()

"""


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
            .replace(" ", "")
            .split(",")
        )
        proficiencies = (
            re.sub(r"\([^)]*\)", "", str(df.at[i, "Proficient"]))
            .upper()
            .replace(" ", "")
            .split(",")
        )
        # longest skill is 6 words long, so if there are any more, delete it because they didn't fill out the survey properly
        for proficiency in proficiencies:
            if len(proficiency.split()) > 6:
                proficiencies = []
                break
        self.skills_ratings = {key: 0 for key in skills}
        for skill in scraped_skills:
            if skill.strip() in self.skills_ratings:
                self.skills_ratings[skill.strip()] = 3
                if skill.strip() in proficiencies:
                    self.skills_ratings[skill.strip()] = 4

        self.preferences: dict[str, int] = {}
        for project in projects:
            self.preferences[project.name] = df.at[i, project.original_name]


LabName: TypeAlias = str
"""Format is 02L, 03L, etc."""


def assign_projects_to_labs(
    projects: list[Project],
    students: list[Student],
    lab_team_count: dict[LabName, int],
    df: pd.DataFrame,
) -> None:
    """Assigns projects to labs based on average lab preference scores

    Modifies the assigned_lab attribute of each project in the projects list based on
    the lab scores in the dataframe.

    Args:
        projects: A list of Project objects to assign to labs
        students: A list of Student objects in the labs that the projects will be
            assigned to.
        lab_team_count: A dictionary mapping lab names to the number of teams in that
            lab.
        df: A pandas dataframe containing the scores for each project in
            each lab. The columns should be labeled with project names and the index
            should be the lab names. The data should be the average
            preference scores.

    Returns:
        None
    """
    lab_preferences: dict[LabName, dict[Project, float]] = {}
    for lab in lab_team_count.keys():
        lab_preferences[lab] = {}
        for project in projects:
            lab_preferences[lab][project] = float(
                str(df.loc[lab, project.original_name])
            )

    lab_skills_ratings: dict[LabName, dict[str, list[float]]] = {
        lab: {skill: [] for skill in project.skills_dict}
        for lab in lab_team_count.keys()
    }
    for student in students:
        for skill in student.skills_ratings:
            lab_skills_ratings[student.lab][skill].append(student.skills_ratings[skill])
    lab_skills_average_ratings: dict[LabName, dict[str, float]] = {
        lab: {
            skill: float(np.mean(ratings))
            for skill, ratings in lab_skills_ratings[lab].items()
        }
        for lab in lab_team_count.keys()
    }
    project_preferences: dict[Project, dict[LabName, float]] = {}
    for project in projects:
        project_preferences[project] = {}
        for lab in lab_team_count.keys():
            project_preferences[project][lab] = 0
            for skill in project.skills_dict:
                if project.skills_dict[skill] == 0:
                    continue
                project_preferences[project][lab] += lab_skills_average_ratings[lab][
                    skill
                ]
            project_preferences[project][lab] = project_preferences[project][lab] / len(
                project.skills_dict
            )

    lab_preferences_order: dict[LabName, list[Project]] = {
        lab: sorted(
            lab_preferences[lab].keys(),
            key=lambda x: lab_preferences[lab][x],
            reverse=True,
        )
        for lab in lab_preferences.keys()
    }
    lab_project_count: dict[LabName, int] = {lab: 0 for lab in lab_team_count.keys()}
    lab_names = list(lab_preferences.keys())
    lab_index = 0
    all_projects_assigned = False
    while not all_projects_assigned:
        for project in projects:
            if not project.assigned_lab:
                break
        else:
            all_projects_assigned = True
            break

        lab = lab_names[lab_index]
        if lab_project_count[lab] == lab_team_count[lab]:
            lab_index += 1 if lab_index != 4 else -4
            continue

        project = lab_preferences_order[lab].pop(0)
        if not project.assigned_lab:
            project.assigned_lab = lab
            lab_project_count[lab] += 1
            continue
        if project_preferences[project][lab] > project_preferences[project][
            project.assigned_lab
        ] or (
            project_preferences[project][lab]
            == project_preferences[project][project.assigned_lab]
            and random.choice([True, False])
        ):
            lab_project_count[project.assigned_lab] -= 1
            project.assigned_lab = lab
            lab_project_count[lab] += 1
            continue


def score_pair(
    student: Student,
    project: Project,
    pref_scalar: int,
) -> tuple[float, float]:
    """Scores a student/project pair based on preference and skills

    Args:
        student: The student to score.
        project: The project to score.
        pref_scalar: An integer scalar to multiply the preference rating by for scoring.
        skills: A list of skills the student or project can have.

    Returns:
        A tuple containing the preference score and skill score of the student/project
        pair.
    """
    skills_weights = {key: 1.0 for key in project.skills_dict.keys()}
    # track how many skills a project requires and which are unfulfilled
    unfulfilled_skills = []
    total_project_skills = 0
    for (
        skill,
        required,
    ) in project.skills_dict.items():
        if not required:
            continue
        total_project_skills += 1

        if all(
            student.skills_ratings[skill] <= 1 for student in project.assigned_students
        ):
            unfulfilled_skills.append(skill)

    # update weights for student skills based on total num skills and num unfulfilled skills
    if unfulfilled_skills:
        num_unfulfilled_skills = len(unfulfilled_skills)
        weight = total_project_skills / num_unfulfilled_skills
        for skill in unfulfilled_skills:
            skills_weights[skill] = weight

    # find skills that current student/project pair both have
    matching_skills = [
        skill
        for skill in student.skills_ratings
        if student.skills_ratings[skill] != 0 and project.skills_dict[skill] != 0
    ]

    preference_score = pref_scalar * student.preferences[project.name]

    skill_score = 0.0
    for matched_skill in matching_skills:
        skill_score += (
            student.skills_ratings[matched_skill] * skills_weights[matched_skill]
        )
    # skill_score /= len(matching_skills) if len(matching_skills) > 0 else 1

    return preference_score, skill_score


def assign_students_to_projects(
    students: list[Student],
    projects: list[Project],
    pref_scalar: int,
) -> None:
    """Assigns students to projects based on preference and skill scores

    Modifies the assigned_project attribute of each student in the students list.

    Args:
        students: A list of Student objects to assign to projects.
        projects: A list of Project objects to assign students to.
        pref_scalar: An integer scalar to multiply the preference rating by for scoring.
        skills: A list of skills the student or project can have.

    Returns:
        None
    """
    assigned_student_count = 0
    while assigned_student_count < len(students):
        max_pair: tuple[Student, Project] = (students[0], projects[0])
        max_score = -1.0
        max_pref_score = -1.0
        for student in students:
            if student.assigned_project:
                continue
            for project in projects:
                if len(project.assigned_students) >= project.team_capacity:
                    continue
                scores = score_pair(student, project, pref_scalar)
                score = sum(scores)
                if score > max_score:
                    max_score = score
                    max_pair = (student, project)
                    max_pref_score = scores[0]
                if score == max_score:  # break ties based on pref score
                    if scores[0] > max_pref_score:
                        max_score = score
                        max_pair = (student, project)
                        max_pref_score = scores[0]

        max_pair[0].assigned_project = max_pair[1].name
        max_pair[1].assigned_students.append(max_pair[0])

        assigned_student_count += 1


def collect_assignment_data(
    students: list[Student],
    projects: list[Project],
    formed_teams_dict: dict[str, list[Any]],
    team_pref_scores: dict[str, list[int]],
) -> tuple[dict[str, list[Any]], dict[str, list[int]]]:
    """
    Collects data about the students and their assigned projects. Modifies the
    formed_teams_dict and team_pref_scores dictionaries

    Args:
        students: A list of Student objects to collect data from.
        projects: A list of Project objects to collect data from.
        formed_teams_dict: A dictionary to append the collected data to.
        team_pref_scores: A dictionary to append the average preference scores to.

    Returns:
        A tuple containing the formed_teams_dict and team_pref_scores dictionaries.
    """
    for student in students:
        # print(f"{student.fn}, {student.ln}")
        # append results to dictionary
        formed_teams_dict["email"].append(student.email)
        formed_teams_dict["student.fn"].append(student.fn)
        formed_teams_dict["student.ln"].append(student.ln)
        formed_teams_dict["lab"].append(student.lab)
        formed_teams_dict["assigned_project"].append(student.assigned_project)
        formed_teams_dict["pref_rating_for_assg_proj"].append(
            student.preferences[student.assigned_project]
        )
        formed_teams_dict["preferences"].append(student.preferences)
        formed_teams_dict["skill_ratings"].append(student.skills_ratings)
        for project in projects:
            if project.name == student.assigned_project:
                # get average preference scores for teams
                member_preference = student.preferences[project.name]
                team_pref_scores[project.name].append(member_preference)

                cur_skills = []
                for skill in list(project.skills_dict.keys()):
                    if project.skills_dict[skill] == 1:
                        cur_skills.append(skill)
        formed_teams_dict["skills_needed_for_project"].append(cur_skills)

    return formed_teams_dict, team_pref_scores


def save_assignment_data(
    team_pref_scores: dict[str, list[int]],
    df_dict: dict[str, list[Any]],
    team_pref_scores_filename: str,
    formed_teams_filename: str,
) -> None:
    """
    Saves the assignment data to a csv file

    Args:
        team_pref_scores: A dictionary mapping project names to a list of preference
            scores of students assigned to that project.
        df_dict: A dictionary containing all the data to be saved to the csv file.
        team_pref_scores_filename: The name of the file to save the team preference
            scores to.
        formed_teams_filename: The name of the file to save the formed teams to.

    Returns:
        None
    """
    # save average preference scores of each project to csv
    team_pref_scores_means: dict[str, float] = {
        project: float(np.mean(scores)) for project, scores in team_pref_scores.items()
    }
    team_pref_scores_list = [
        {"team": team, "score": score} for team, score in team_pref_scores_means.items()
    ]
    team_pref_scores_df = pd.DataFrame(team_pref_scores_list)
    team_pref_scores_df.to_csv(team_pref_scores_filename)

    df_flat = pd.DataFrame(df_dict).copy()
    for column in df_flat.columns:
        if isinstance(df_flat[column].iloc[0], dict):
            expanded_df = df_flat[column].apply(pd.Series)
            expanded_df = expanded_df.add_prefix(f"{column} - ")
            df_flat = df_flat.drop(column, axis=1).join(expanded_df)

    # remove columns irrelevant to spreadsheet analysis
    df_flat = df_flat.drop(columns=["email"])

    # move less important columns to end of df
    move_cols = ["skills_needed_for_project"]
    df_flat = df_flat[
        [col for col in df_flat.columns if col not in move_cols] + move_cols
    ]

    df_flat.to_csv(formed_teams_filename)  # save as csv


ProjectName: TypeAlias = str
AssignedPreferences: TypeAlias = dict[ProjectName, float]
ClasswidePreferences: TypeAlias = dict[ProjectName, float]


def plot_histogram(
    skills_percent: dict,
    classwide_skill_frequency: dict,
    avg_prefs: tuple[AssignedPreferences, ClasswidePreferences],
    histogram_filename: str,
) -> None:
    """
    Plots a histogram of the projects' fulfilled skills and average preference scores

    Compared to the classwide averages

    Args:
        skills_percent: A dictionary mapping project names to the percentage of required
            skills fulfilled by the assigned students.
        classwide_skill_frequency: A dictionary mapping project names to the average number
            of skills fulfilled by students in the class.
        avg_prefs: A tuple containing two dictionaries. The first dictionary maps project
            names to the average preference score of assigned students. The second dictionary
            maps project names to the average preference score of all students.
        histogram_filename: The name of the file to save the histogram to.

    Returns:
        None
    """
    # print stddevs and average of all team preference scores and % of skills fulfille
    fulfilled_average: float = np.mean(list(skills_percent.values()))
    fulfilled_stdev: float = np.std(list(skills_percent.values()))
    # write average team preference and stdev
    preference_average: float = np.mean(list(avg_prefs[0].values()))
    preference_stdev: float = np.std(list(avg_prefs[0].values()))
    print(
        f"Average % of fulfilled skills: {fulfilled_average:.2f} ± {fulfilled_stdev:.2f}"
    )
    print(
        f"Average preference score of teams: {preference_average:.2f} ± {preference_stdev:.2f}"
    )

    bins = list(avg_prefs[0].keys())
    x = np.arange(len(bins))
    width = 0.4
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()

    ax1.bar(
        x - width / 2,
        list(skills_percent.values()),
        width,
        label=r"Project Skills Fulfilled",
        color="gold",
    )
    ax1.set_xlabel("Project Teams", fontsize=15)
    ax1.set_ylabel("Project Skills Fulfilled", fontsize=15)
    ax1.set_yticks(np.arange(0, 110, 10), minor=True)
    ax1.set_axisbelow(True)
    ax1.grid(axis="y", which="major", color="black", linestyle="--", linewidth=1)
    ax1.grid(axis="y", which="minor", color="gray", linestyle="--", linewidth=0.5)
    ax1.set_ylim(0, 106)

    for i, proj in enumerate(bins):
        cur_avg = classwide_skill_frequency[proj]
        ax1.scatter(
            x[i] - width / 2,
            cur_avg,
            color="orange",
            marker="o",
            s=60,
            label="Global Average Skill Frequency" if i == 0 else "",
        )

    ax2.bar(
        x + width / 2,
        list(avg_prefs[0].values()),
        width,
        label="Student Preference Toward Assignment",
        color="#003366",
    )
    ax2.set_ylabel("Average Preference Score of Teams (1-5)", fontsize=15)
    ax2.set_ylim(0, 5.3)
    ax2.set_yticks(np.arange(0, 5.5, 0.5), minor=True)

    for i, proj in enumerate(bins):
        cur_avg = avg_prefs[1][proj]
        ax2.scatter(
            x[i] + width / 2,
            cur_avg,
            color="lightblue",
            marker="D",
            s=60,
            label="Global Average Project Preferences" if i == 0 else "",
        )

    anonymized = [f"P{i}" for i in range(1, len(skills_percent) + 1)]

    ax1.set_xticks(x)
    ax1.set_xticklabels(anonymized, rotation=30, ha="right", fontsize=12)

    plt.title(" ")
    # fig.legend(loc="upper center", ncol=4, bbox_to_anchor=(0.5, 1.01), fontsize=24, framealpha=1)
    plt.tight_layout()
    fig.savefig(histogram_filename, dpi=300)

def clean_data_for_silly_mongo(item: Any) -> Any:
    """
    Converts numpy types to native Python types for MongoDB compatibility

    Args:
        item: The item to clean.
    Returns:
        The cleaned item.
    """
    if isinstance(item, dict):
        return {k: clean_data_for_silly_mongo(v) for k, v in item.items()}
    elif isinstance(item, list):
        return [clean_data_for_silly_mongo(elem) for elem in item]
    elif isinstance(item, np.integer):
        return int(item)
    elif isinstance(item, np.floating):
        return float(item)
    elif isinstance(item, np.ndarray):
        return item.tolist()
    else:
        return item


def push_results_to_db(
    collection: pymongo.collection.Collection, formed_teams_dict: defaultdict
) -> None:
    """
    Pushes the formed teams data to the MongoDB database

    Args:
        collection: The collection to push the data to.
        formed_teams_dict: A dictionary containing the formed teams data.

    Returns:
        None
    """
    students_to_insert = []
    for i in range(len(formed_teams_dict["assigned_project"])):
        print(f"Inserting student {i} into database")
        student_document = {
            "email": formed_teams_dict["email"][i],
            "student_fn": formed_teams_dict["student.fn"][i],
            "student_ln": formed_teams_dict["student.ln"][i],
            "assigned_project": formed_teams_dict["assigned_project"][i],
            "score_for_assg_project": float(
                formed_teams_dict["score_for_project"][i]
            ),  # mongo can't handle np arrs
            "scores_for_all_projects": formed_teams_dict["score_for_all_projects"][i],
            "proficiencies": formed_teams_dict["proficient"][i],
            "preferences": formed_teams_dict["preferences"][i],
            "skill_ratings": formed_teams_dict["skill_ratings"][i],
            "lab_section": formed_teams_dict["lab"][i],
            "project_skills_required": formed_teams_dict["skills_needed_for_project"][
                i
            ],
        }
        students_to_insert.append(student_document)

    # mongodb is picky about datatypes it can store
    cleaned_students_to_insert = clean_data_for_silly_mongo(students_to_insert)

    for student_document in cleaned_students_to_insert:
        # Use update_one with upsert=True to either update existing document or insert new one
        result = collection.update_one(
            {
                "_id": student_document["_id"]
            },  # Query part: checks if the _id already exists
            {
                "$set": student_document
            },  # Update part: sets the document to the new values
            upsert=True,  # Upsert option: insert if _id does not exist
        )

        if result.matched_count:
            print(f"Updated document with _id: {student_document['_id']}")
        elif result.upserted_id:
            print(f"Inserted new document with _id: {student_document['_id']}")


def autolabel_histogram(ax: plt.Axes, bars: list[plt.Rectangle]) -> None:
    """Labels bars with heights on a histogram

    Args:
        ax: The axes object to annotate.
        bars: A list of bar objects to annotate.

    Returns:
        None
    """
    for bar in bars:
        h = bar.get_height()
        if h < 10:
            annotate_text = f"{h:.1f}"
        else:
            annotate_text = f"{int(h)}"

        ax.annotate(
            annotate_text,
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=7,
        )


TeamSizes: TypeAlias = list[int]
"""A list of the number of students in each team for a lab."""


def size_teams_with_labs(
    lab_populations: dict[LabName, int], base_team_size: int
) -> dict[str, TeamSizes]:
    """Assigns team sizes to labs given a base team size

    Args:
        lab_populations: A list of the populations of each lab.
        base_team_size: The base size of each team.

    Returns:
        A dictionary mapping lab names to a list of team sizes.
    """
    lab_team_count = {
        lab: (population // base_team_size)
        for lab, population in lab_populations.items()
    }
    lab_team_sizes: dict[str, TeamSizes] = {}
    for lab, num_teams in lab_team_count.items():
        lab_team_sizes[lab] = [base_team_size] * num_teams

        remaining = lab_populations[lab] - num_teams * base_team_size
        lab_team_sizes[lab] = [
            lab_team_sizes[lab][j] + remaining // num_teams for j in range(num_teams)
        ]
        remaining = remaining % num_teams
        for j in range(remaining):
            lab_team_sizes[lab][j] += 1

        for j, size in enumerate(lab_team_sizes[lab]):
            if size > 6:
                lab_team_sizes[lab][j] = size // 2
                lab_team_sizes[lab].append(size // 2 + size % 2)

    return lab_team_sizes


def form_teams(
    student_data_file: str,
    student_skills_file: str,
    project_skills_file: str,
    base_team_size: int,
    skills_file: str,
    client: Optional[pymongo.MongoClient] = None,
    formed_teams_filename: str = "output/formed_teams.csv",
    team_pref_scores_filename: str = "output/team_pref_scores.csv",
    histogram_filename: Optional[str] = None,
    option: Optional[int] = None,
    seed: Optional[int] = None,
) -> None:
    """Assigns students to projects using spreadsheet skill and preference data

    Args:
        student_data_file: The name of the file containing student data.
        lab_team_count: A list of the populations of each lab.
        base_team_size: The base size of each team.
        skills_file: The name of the file containing the skills data.
        client: The MongoDB client to push the data to.
        formed_teams_filename: The name of the file to save the formed teams to.
        team_pref_scores_filename: The name of the file to save the team preference
            scores to.
        histogram_filename: The name of the file to save the histogram to.
        option: The option to use for team distribution.

    Returns:
        None
    """

    if seed is not None:
        random.seed(seed)

    # PHASE 1: ASSIGNING TEAM SIZES TO LABS
    student_df = pd.read_excel(
        student_data_file,
        sheet_name="SURVEY NODU+STAT",
        index_col=None,
    )

    lab_populations: dict[LabName, int] = {}
    for i in range(len(student_df)):
        lab = student_df.at[i, "Lab"]
        if pd.isna(lab):
            break
        lab_populations[lab] = lab_populations.get(lab, 0) + 1

    first_labname = list(lab_populations.keys())[0]
    labless_lab_populations: dict[LabName, int] = {
        first_labname: sum(lab_populations.values())
    }
    teams_distribution_options: dict[int, dict[LabName, TeamSizes]] = {}
    teams_distribution_options[1] = size_teams_with_labs(
        lab_populations, base_team_size
    )
    teams_distribution_options[2] = size_teams_with_labs(
        lab_populations, base_team_size
    )
    teams_distribution_options[3] = size_teams_with_labs(
        labless_lab_populations, base_team_size
    )

    opt: Optional[int] = option
    if opt is None:
        pprint(teams_distribution_options)
        opt = int(input("\nWhich option is preferable? (Enter 1, 2, or 3) "))
    skip_labs: bool = opt == 3
    lab_team_sizes: dict[LabName, TeamSizes] = teams_distribution_options[opt]

    lab_team_sizes = {
        "02L": [5, 5, 4, 4, 3],
        "03L": [5, 5, 5, 4, 4, 3],
        "04L": [5, 5, 5, 5, 4, 4],
        "05L": [5, 5, 5, 5, 4],
        "06L": [5, 5, 5, 5, 5],
    }

    # PHASE 2: PARSING AND INITIALIZING DATA
    with open(skills_file, "r") as f:
        SKILLS = f.read().replace(" ", "").splitlines()

    project_df = pd.read_excel(
        student_data_file,
        sheet_name="Averages",
        index_col="index",
    )

    projects: list[Project] = [
        Project(name, SKILLS) for name in project_df.columns[:-4]
    ]

    # project duplication, skill insertion
    """ this file should have 3 attributes     "presentation_skills": team numbers with a list of corresponding skills
     "duplicates": list of projects with the same preference scores and names
     "acronym_team_numbers": list of project acronyms and the corresponding team number,
         if project was duplicated, name is appended with _1 for the first instance and
         _2 for the second
    """
    with open(project_skills_file, "r") as f:
        data = json.load(f)
    duplicates: list[str] = data["duplicates"]
    presentation_skills: dict[int, list[str]] = {
        int(key): value for key, value in data["presentation_skills"].items()
    }
    acronym_team_numbers: dict[str, int] = {
        key: value for key, value in data["acronym_team_numbers"].items()
    }

    for project in projects:
        if project.name in duplicates:
            projects.append(copy.deepcopy(project))
            project.name = f"{project.name}_1"
            projects[-1].name = f"{projects[-1].name}_2"

    project_skills: dict[str, list[str]] = {}
    for project in projects:
        if project.original_name in duplicates:
            project_skills[project.name] = list(
                set(
                    presentation_skills[
                        acronym_team_numbers[f"{project.original_name}_1"]
                    ]
                    + presentation_skills[
                        acronym_team_numbers[f"{project.original_name}_2"]
                    ]
                )
            )
            continue
        project_skills[project.name] = presentation_skills[
            acronym_team_numbers[project.original_name]
        ]

    for project in projects:
        project.skills_dict = {skill: 0 for skill in SKILLS}
        ### skills from the json file are formatted with spaces, but not in the skill object
        for skill in project_skills[project.name]:
            project.skills_dict[skill.replace(" ", "")] = 1

    # remove project excess projects
    team_count = 0
    for lab in lab_team_sizes.keys():
        team_count += len(lab_team_sizes[lab])
    while len(projects) > team_count:
        projects.pop()

    students: list[Student] = []
    # last row is nan, first row is headers
    for i in range(len(student_df) - 2):
        s = Student(student_df, projects, i, SKILLS)
        if skip_labs:
            s.lab = first_labname

        # student_data/student_skills.json has key student name and value list of skills that should have a rating of 5
        with open(student_skills_file, "r") as f:
            student_skills = json.load(f)
        for skill in student_skills[s.fn + " " + s.ln]:
            formatted_skill = skill.replace(" ", "").upper()
            s.skills_ratings[formatted_skill] = 5

        students.append(s)

    assign_projects_to_labs(
        projects,
        students,
        {key: len(value) for key, value in lab_team_sizes.items()},
        project_df,
    )

    # # for testing purposes, randomly assign projects to labs, ensuring not to exceed team capacity
    # labs = {lab: len(lab_team_sizes[lab]) for lab in lab_team_sizes.keys()}
    # for project in projects:
    #     random_lab = random.choice(list(labs.keys()))
    #     project.assigned_lab = random_lab
    #     labs[random_lab] -= 1
    #     if labs[random_lab] == 0:
    #         labs.pop(random_lab)


    # average preference scores of all students for each project
    # needed in case there are no labs, regardless of skip labs later saved in data collection
    classwide_preferences: dict[ProjectName, float] = {}
    for project in projects:
        preference = 0
        for student in students:
            preference += student.preferences[project.name]
        classwide_preferences[project.name] = preference / len(students)

    # give projects sizes based on preference
    if skip_labs:
        # sort projects by classwide preference scores
        projects = sorted(
            projects,
            key=lambda project: classwide_preferences[project.name],
            reverse=True,
        )
        for i, project in enumerate(projects):
            project.team_capacity = lab_team_sizes[first_labname][i]
    else:
        for lab in lab_team_sizes.keys():
            lab_projects = [
                project for project in projects if project.assigned_lab == lab
            ]
            for i in range(len(lab_projects)):
                lab_projects[i].team_capacity = lab_team_sizes[lab][i]

    formed_teams_dict: dict[str, list[Any]] = defaultdict(list)
    team_pref_scores: dict[str, list[int]] = defaultdict(list)

    # PHASE 3: ASSIGNING STUDENTS TO PROJECTS
    PREF_SCALAR: int = 10
    for lab in lab_team_sizes.keys():
        # group students and project by lab
        cur_students: list[Student] = [
            student for student in students if student.lab == lab
        ]
        cur_projects: list[Project] = [
            project for project in projects if project.assigned_lab == lab
        ]
        # # randomly assign students to projects
        # for student in cur_students:
        #     random_project = random.choice(cur_projects)
        #     student.assigned_project = random_project.name
        #     random_project.assigned_students.append(student)
        #     if len(random_project.assigned_students) == random_project.team_capacity:
        #         cur_projects.pop(cur_projects.index(random_project))

        assign_students_to_projects(cur_students, cur_projects, PREF_SCALAR)

    #     # # collect data for phase 4
    #     # formed_teams_dict, team_pref_scores = collect_assignment_data(
    #     #     cur_students, cur_projects, formed_teams_dict, team_pref_scores
    #     # )

    # with open("assignments.json", "r") as f:
    #     assignments = json.load(f)
    # student_emails_dict = {student.email: student for student in students}
    # project_names = {project.name: project for project in projects}
    # # assignments has key project name, value list of student emails
    # for project_name, student_emails in assignments.items():
    #     for email in student_emails:
    #         student = student_emails_dict[email]
    #         student.assigned_project = project_name
    #         project = project_names[project_name]
    #         project.assigned_students.append(student)

    # # PHASE 4: SAVING AND PLOTTING RESULTS
    # save_assignment_data(
    #     team_pref_scores,
    #     formed_teams_dict,
    #     team_pref_scores_filename,
    #     formed_teams_filename,
    # )

    # average preference scores of assigned team members for each project
    avg_assigned_prefs: dict[ProjectName, float] = {}
    for project in projects:
        cur_assigned_prefs = []
        for student in students:
            if student.assigned_project == project.name:
                cur_assigned_prefs.append(student.preferences[project.name])

        avg_assigned_prefs[project.name] = float(np.mean(cur_assigned_prefs))

    # percentage of required skills fulfilled for each project by the team
    project_fulfilled_skills_percent = {}
    for project in projects:
        cur_prefs = []
        cur_skills = []
        for student in students:
            if student.assigned_project == project.name:
                cur_prefs.append(student.preferences[project.name])
                cur_skills.append(student.skills_ratings)

        required_skills = {
            skill for skill, required in project.skills_dict.items() if required == 1
        }
        team_skills = set()
        for student_skill in cur_skills:
            for skill, rating in student_skill.items():
                if rating > 1:
                    team_skills.add(skill)

        fulfilled_skills = required_skills.intersection(team_skills)
        project_fulfilled_skills_percent[project.name] = int(
            100 * (len(fulfilled_skills) / len(required_skills))
        )

    """
    A student is considered to have a skill if their rating is greater than 1 (in
    alignment with other parts of the code). A project's skill frequency
    (project_skill_frequency) is the average percentage of students who have each
    required skill.

    Example:
        If a project requires skills A, B, and C, and 50% of students have skill A, 75%
        have skill B, and 25% have skill C, then the project's skill frequency would be
        50 + 75 + 25 / 3 = 50%
    """
    # frequency of each skill among students
    skill_frequency: dict[str, float] = {SKILLS[i]: 0.0 for i in range(len(SKILLS))}
    for student in students:
        for skill, rating in student.skills_ratings.items():
            if rating > 1:
                skill_frequency[skill] += 1
    for skill in skill_frequency:
        skill_frequency[skill] = (skill_frequency[skill] / len(students)) * 100
    project_skill_frequency: dict[ProjectName, float] = {}
    for project in projects:
        required_skills = {
            skill for skill, required in project.skills_dict.items() if required == 1
        }
        fulfilled_skill_percentage = 0.0
        for skill in required_skills:
            fulfilled_skill_percentage += skill_frequency[skill]
        project_skill_frequency[project.name] = fulfilled_skill_percentage / len(
            required_skills
        )

    if histogram_filename:
        plot_histogram(
            project_fulfilled_skills_percent,
            project_skill_frequency,
            (
                avg_assigned_prefs,
                classwide_preferences,
            ),
            histogram_filename,
        )

    if not client:
        return
    """ push results to db """
    semester = "spring23"
    collection = client["assg_students"][semester]
    # push_results_to_db(collection, formed_teams_dict)
