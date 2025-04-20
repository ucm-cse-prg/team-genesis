import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import PIL
from parse_data import parse_data
from assign_students import assign_students
from output_data import plot_histogram
import copy

# 2d array, true and false
@pytest.mark.parametrize(
    "pref_scalar, anonymized",
    [
        (0, False),
        (10, False),
        (20, False),
        (30, False),
        (40, False),
        (50, False),
        (0, True),
        (10, True),
        (20, True),
        (30, True),
        (40, True),
        (50, True),
    ],
)
def test_image(pref_scalar, anonymized):
    """Test the algorithm with different preference scores."""
    students, projects = parse_data(
        student_project_data_file="student_data/2025-01-Spring-CSE-MASTER.xlsx"
    )
    assign_students(students, projects, base_team_size=5, seed=42, pref_scalar=pref_scalar)
    plot_histogram(students, projects, f"tests/test_histogram_{pref_scalar}.png", anonymize=anonymized)
    with open(f"tests/test_histogram_{pref_scalar}.png", "rb") as f:
        img = copy.deepcopy(PIL.Image.open(f))
    os.remove(f"tests/test_histogram_{pref_scalar}.png")
    with open(f"tests/data/{'anonymized_' if anonymized else ''}histogram_{pref_scalar}.png", "rb") as f:
        expected_img = copy.deepcopy(PIL.Image.open(f))
    assert img == expected_img, f"{'Anonymous Test' if anonymized else 'Test'} failed for preference score {pref_scalar}."

    # actually I also need to write tests for anonymized version