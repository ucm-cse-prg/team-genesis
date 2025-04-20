import matplotlib.pyplot as plt
import numpy as np
from typing import TypeAlias
from datatypes import Student, Project

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


def skill_fulfillment_percentage(
    students: list[Student], skill: str, threshold: int = 6
) -> float:
    """
    Calculates the percentage of students who have a skill rating above a certain threshold.

    Args:
        students: A list of Student objects.
        skill: The skill to check.
        threshold: The rating threshold.

    Returns:
        The percentage of students with the skill rating above the threshold.
    """
    total_students = len(students)
    if total_students == 0:
        return 0.0
    fulfilling_student_count = 0
    for student in students:
        if skill in student.skills_ratings:
            if student.skills_ratings[skill] >= threshold:
                fulfilling_student_count += 1

    return (fulfilling_student_count / total_students) * 100


def plot_histogram(
    students: list[Student],
    projects: list[Project],
    histogram_filename: str,
    anonymize: bool = False,
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

    skills_percent: dict[ProjectName, float] = {}
    classwide_skill_frequency: ClasswidePreferences = {}
    assigned_prefs: AssignedPreferences = {}
    classwide_prefs: ClasswidePreferences = {}
    for project in projects:
        skills_percent[project.name] = float(
            np.mean(
                [
                    skill_fulfillment_percentage(project.assigned_students, skill) > 0
                    for skill in project.skills_dict
                    if project.skills_dict[skill] == 1
                ]
            )
            * 100
        )
        classwide_skill_frequency[project.name] = float(
            np.mean(
                [
                    skill_fulfillment_percentage(students, skill)
                    for skill in project.skills_dict
                    if project.skills_dict[skill] == 1
                ]
            )
        )
        assigned_prefs[project.name] = float(
            np.mean(
                [
                    student.preferences[project.name]
                    for student in project.assigned_students
                ]
            )
        )
        classwide_prefs[project.name] = float(
            np.mean([student.preferences[project.name] for student in students])
        )
    avg_prefs = (assigned_prefs, classwide_prefs)

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

    project_labels: list[str] = [project.name for project in projects]
    if anonymize:
        project_labels = [f"P{i}" for i in range(1, len(project_labels) + 1)]

    ax1.set_xticks(x)
    ax1.set_xticklabels(project_labels, rotation=30, ha="right", fontsize=12)

    plt.title(" ")
    # fig.legend(loc="upper center", ncol=4, bbox_to_anchor=(0.5, 1.01), fontsize=24, framealpha=1)
    plt.tight_layout()
    fig.savefig(histogram_filename, dpi=300)
