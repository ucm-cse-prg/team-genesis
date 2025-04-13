from datatypes import Student, Project
from parse_data import parse_data
from assign_students import assign_students
# from output_data import analyze_results, output_results

if __name__ == "__main__":
    SEED=42
    STUDENT_PROJECT_DATA_FILE = "student_data/2025-01-Spring-CSE-MASTER.xlsx"
    SKILLS_FILE = "student_data/SKILLS_LIST_S25.txt"

    students: list[Student]
    projects: list[Project]
    students, projects = parse_data(STUDENT_PROJECT_DATA_FILE, SKILLS_FILE)
    assign_students(students, projects, base_team_size=5, seed=SEED)
            
    # output_results(students, projects, "output/results.txt")
    # analyze_results(students, projects, "output/result_metrics_plotted.png")
