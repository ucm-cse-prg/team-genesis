from datatypes import Student, Project
from parse_data import parse_data
from assign_students import assign_students
from output_data import write_to_file, plot_histogram

if __name__ == "__main__":
    students: list[Student]
    projects: list[Project]
    students, projects = parse_data(
        student_project_data_file="student_data/2025-01-Spring-CSE-MASTER.xlsx"
    )
    assign_students(students, projects, base_team_size=5, seed=42, pref_scalar=20)
    write_to_file(projects, filename="output/results.txt")
    plot_histogram(students, projects, "output/skill_histogram.png")

# TODO: need duplication/deletion prio list from api
