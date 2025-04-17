from datatypes import Student, Project
from parse_data import parse_data
from assign_students import assign_students
from output_data import write_to_file

if __name__ == "__main__":
    students: list[Student]
    projects: list[Project]
    students, projects = parse_data(
        student_project_data_file="student_data/2025-01-Spring-CSE-MASTER.xlsx",
        skills_file="student_data/SKILLS_LIST_S25.txt",
    )
    assign_students(students, projects, base_team_size=5, seed=42)
    write_to_file(projects, filename="output/results.txt")

    # analyze_results(students, projects, "output/result_metrics_plotted.png")
