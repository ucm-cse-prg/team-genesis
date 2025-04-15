from datatypes import Student, Project, LabName
from typing import Optional
import numpy as np
import random
from collections import defaultdict
from typing import TypeAlias, Any

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
            student.skills_ratings[skill] <= 5 for student in project.assigned_students
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

    return preference_score, skill_score

# TODO: need refactoring and better name because this is the basically the same as the main thing "assign_students"
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
                    if scores[0] == max_pref_score and random.choice([True, False]):
                        max_score = score
                        max_pair = (student, project)
                        max_pref_score = scores[0]

        max_pair[0].assigned_project = max_pair[1].name
        max_pair[1].assigned_students.append(max_pair[0])

        assigned_student_count += 1

TeamSizes: TypeAlias = list[int]
"""A list of the number of students in each team for a lab."""

def assign_students(students: list[Student], projects: list[Project], base_team_size: int = 5, pref_scalar: int = 20, seed: Optional[int] = None) -> None:
    """Assigns students to projects based on their preferences and skills.
    Mutates the passed students and projects.
    
    Args:
        students (list[Student]): A list of students to be assigned to projects.
        projects (list[Project]): A list of projects to assign students to.

    Returns:
        None
    """

    lab_populations: dict[LabName, int] = {}
    for student in students:
        if student.lab not in lab_populations:
            lab_populations[student.lab] = 0
        lab_populations[student.lab] += 1

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


    lab_preferences: dict[LabName, dict[Project, float]] = {}
    for lab in lab_team_count.keys():
        lab_preferences[lab] = {}
        for student in students:
            if student.lab == lab:
                for project in projects:
                    if project.name not in lab_preferences[lab]:
                        lab_preferences[lab][project] = 0
                    lab_preferences[lab][project] += student.preferences[
                        project.name
                    ]
                lab_preferences[lab][project] = (
                    lab_preferences[lab][project] / len(students)
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
            lab_index += 1 if lab_index != 5 else -5
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

    classwide_preferences: dict[str, float] = {}
    for project in projects:
        preference = 0
        for student in students:
            preference += student.preferences[project.name]
        classwide_preferences[project.name] = preference / len(students)

    for lab in lab_team_sizes.keys():
        lab_projects = [
            project for project in projects if project.assigned_lab == lab
        ]
        for i in range(len(lab_projects)):
            lab_projects[i].team_capacity = lab_team_sizes[lab][i]

    formed_teams_dict: dict[str, list[Any]] = defaultdict(list)
    team_pref_scores: dict[str, list[int]] = defaultdict(list)

    # PHASE 3: ASSIGNING STUDENTS TO PROJECTS
    for lab in lab_team_sizes.keys():
        # group students and project by lab
        cur_students: list[Student] = [
            student for student in students if student.lab == lab
        ]
        cur_projects: list[Project] = [
            project for project in projects if project.assigned_lab == lab
        ]
        assign_students_to_projects(cur_students, cur_projects, pref_scalar=pref_scalar)
