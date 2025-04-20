import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from parse_data import parse_data
from assign_students import assign_students
from output_data import write_to_file


@pytest.mark.parametrize(
    "pref_scalar",
    [0, 10, 20, 30, 40, 50],
)
def test_algorithm(pref_scalar):
    """Test the algorithm with different preference scores."""
    students, projects = parse_data(
        student_project_data_file="student_data/2025-01-Spring-CSE-MASTER.xlsx"
    )
    assign_students(students, projects, base_team_size=5, seed=42, pref_scalar=pref_scalar)
    write_to_file(projects, filename=f"tests/test_results_{pref_scalar}.txt")
    with open(f"tests/test_results_{pref_scalar}.txt", "r") as f:
        lines = f.readlines()
    os.remove(f"tests/test_results_{pref_scalar}.txt") 
    with open(f"tests/data/test_results_{pref_scalar}.txt", "r") as f:
        expected_lines = f.readlines()

    assert lines == expected_lines, f"Test failed for preference score {pref_scalar}."

