from datatypes import Student, Project, LabName
from typing import Dict, Any
from docplex.mp.model import Model  # type: ignore
import time


def assign_students(
    students: list[Student],
    projects: list[Project],
    base_team_size: int,
    pref_scalar: float = 0.5,
    optimal_gap: float = 0.01,
) -> None:
    # create CPLEX model
    model = Model(name="assign_students")
    # decision variables for student-project assignment
    student_project_assignment: Dict[tuple, Any] = {
        (student, project): model.binary_var(name=f"x_{student.email}_{project.name}")
        for student in students
        for project in projects
    }

    # many-to-one assignment
    for student in students:
        model.add_constraint(
            model.sum(student_project_assignment[(student, project)] for project in projects) == 1,
            ctname=f"OneProjectPerStudent_{student.email}",
        )
    for project in projects:
        model.add_constraint(
            model.sum(student_project_assignment[(student, project)] for student in students) == base_team_size,
            ctname=f"MaxTeamSize_{project.name}",
        )

    # lab restriction
    labs: list[LabName] = list(set(student.lab for student in students))
    labs.sort()
    lab_assignments: Dict[tuple, Any] = {
        (lab, project): model.binary_var(name=f"y_{lab}_{project.name}")
        for lab in labs
        for project in projects
    }
    for project in projects:
        model.add_constraint(
            model.sum(lab_assignments[(lab, project)] for lab in labs) == 1,
            ctname=f"OneLabPerProject_{project.name}",
        )
    for project in projects:
        for student in students:
            model.add_constraint(
                student_project_assignment[(student, project)]
                <= lab_assignments[(student.lab, project)],
                ctname=f"LabAssignment_{student.email}_{project.name}",
            )

    # student preference objective
    # student preference objective
    total_student_preference = model.sum(
        student_project_assignment[(student, project)] * student.preferences[project.name]
        for student in students
        for project in projects
    ) / 9

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
    project_skill_fulfilled: Dict[tuple, Any] = {
        (project, skill): model.binary_var(name=f"z_{project.name}_{skill}")
        for project in projects
        for skill in skills
    }
    for project in projects:
        for skill in required_skills[project]:
            model.add_constraint(
                model.sum(
                    student_project_assignment[(student, project)] * fulfills_skill[student].get(skill, 0)
                    for student in students
                ) >= project_skill_fulfilled[(project, skill)],
                ctname=f"SkillFulfillment_{project.name}_{skill}",
            )

    total_skill_fulfillment = (
        model.sum(
            project_skill_fulfilled[(project, skill)] * (1.0 / len(required_skills[project]))
            for project in projects
            for skill in required_skills[project]
        )
        * 100
        / len(projects)
    )

    # set objective to maximize combined preference and skill fulfillment
    model.maximize(total_student_preference * pref_scalar + total_skill_fulfillment * (1 - pref_scalar))

    # configure CPLEX parameters and solve
    model.parameters.timelimit = 60
    model.parameters.mip.tolerances.mipgap = optimal_gap
    model.parameters.threads = 32
    start = time.time()
    print(f"Starting CPLEX solver at time: {time.strftime('%I:%M:%S %p')}")
    solution = model.solve(log_output=False)
    end = time.time()
    print(f"CPLEX solver time: {end - start:.2f} seconds")
    
    if solution is None:
        raise RuntimeError("No solution found by CPLEX")

    # extract solution assignments
    for student in students:
        for project in projects:
            var = student_project_assignment[(student, project)]
            # use solution object to get variable value
            if solution.get_value(var) > 0.5:
                student.assigned_project = project.name
                project.assigned_students.append(student)
                project.assigned_lab = student.lab
                project.team_capacity = base_team_size
                break

    # Print the results
    print("Student Assignments:")
    for student in students:
        print(f"{student.fn} {student.ln} -> {student.assigned_project}")