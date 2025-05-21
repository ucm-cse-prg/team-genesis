from datatypes import Student, Project, LabName
from typing import Optional, Dict
from pulp import (
    LpProblem,
    LpMaximize,
    LpVariable,
    lpSum,
    LpBinary,
    LpAffineExpression,
    PULP_CBC_CMD,
)
import time


def assign_students(
    students: list[Student],
    projects: list[Project],
    base_team_size: int,
    pref_scalar: float = 0.5,
    optimal_gap: float = 0.01,
) -> None:
    problem: LpProblem = LpProblem("problem", LpMaximize)
    student_project_assignment: Dict[Student, Dict[Project, LpVariable]] = (
        LpVariable.dicts("x", (students, projects), cat=LpBinary)
    )

    # many-to-one assignment
    for student in students:
        problem += (
            lpSum(student_project_assignment[student][project] for project in projects)
            == 1,
            f"OneProjectPerStudent_{student.email}",
        )
    for project in projects:
        problem += (
            lpSum(student_project_assignment[student][project] for student in students)
            == base_team_size,
            f"MaxTeamSize_{project.name}",
        )

    # lab restriction
    labs: list[LabName] = list(set(student.lab for student in students))
    labs.sort()
    lab_assignments: Dict[LabName, Dict[Project, LpVariable]] = LpVariable.dicts(
        "y", (labs, projects), cat=LpBinary
    )
    for project in projects:
        problem += (
            lpSum(lab_assignments[lab][project] for lab in labs) == 1,
            f"OneLabPerProject_{project.name}",
        )
    for project in projects:
        for student in students:
            problem += (
                student_project_assignment[student][project]
                <= lab_assignments[student.lab][project],
                f"LabAssignment_{student.email}_{project.name}",
            )

    # student preference objective
    total_student_preference: LpAffineExpression = (
        lpSum(
            student_project_assignment[student][project]
            * student.preferences[project.name]
            for student in students
            for project in projects
        )
        / 9
    )

    # skill fulfillment objective
    skills = list(set(projects[0].skills_dict.keys()))
    required_skills: Dict[Project, list[str]] = {
        project: [
            skill for skill in project.skills_dict if project.skills_dict[skill] == 1
        ]
        for project in projects
    }
    fulfills_skill: Dict[Student, Dict[str, int]] = {
        student: {
            skill: 1
            for skill in student.skills_ratings
            if student.skills_ratings[skill] >= 6
        }
        for student in students
    }
    project_skill_fulfilled: Dict[Project, Dict[str, LpVariable]] = LpVariable.dicts(
        "z", (projects, skills), cat=LpBinary
    )
    for project in projects:
        for skill in required_skills[project]:
            problem += (
                lpSum(
                    student_project_assignment[student][project]
                    * fulfills_skill[student].get(skill, 0)
                    for student in students
                )
                >= project_skill_fulfilled[project][skill],
                f"SkillFulfillment_{project.name}_{skill}",
            )

    total_skill_fulfillment: LpAffineExpression = (
        lpSum(
            project_skill_fulfilled[project][skill]
            * (1.0 / len(required_skills[project]))
            for project in projects
            for skill in required_skills[project]
        )
        * 100
        / len(projects)
    )

    problem += (
        total_student_preference * pref_scalar
        + total_skill_fulfillment * (1 - pref_scalar),
        "Objective",
    )

    start = time.time()
    print(f"Starting solver at time: {time.strftime('%I:%M:%S %p')}")
    problem.solve(PULP_CBC_CMD(msg=False, timeLimit=60, threads=32, gapRel=optimal_gap))
    end = time.time()
    print(f"Solver time: {end - start:.2f} seconds")

    for student in students:
        for project in projects:
            if student_project_assignment[student][project].varValue == 1:
                student.assigned_project = project.name
                project.assigned_students.append(student)
                project.assigned_lab = student.lab
                project.team_capacity = base_team_size
                break
