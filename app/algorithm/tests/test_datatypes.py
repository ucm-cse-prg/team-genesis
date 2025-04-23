import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from hypothesis import given, strategies as st
from datatypes import Project


@pytest.mark.parametrize(
    "name, team_number, skills_dict, original_name",
    [
        ("Project", 1, {"skill1": 1, "skill2": 0}, "Project"),
        ("Project_1", 2, {"skill3": 1, "skill4": 0}, "Project"),
        ("XAOE", 3, {"skill5": 1, "skill4": 0}, "XAOE"),
        ("XAOE_2", 3, {"skill1": 1, "skill2": 0}, "XAOE"),
    ],
)
def test_project_init(name: str, team_number: int, skills_dict: dict[str, int], original_name: str) -> None:
    project = Project(name, team_number, skills_dict)

    assert project.name == name
    assert project.original_name == original_name
    assert project.skills_dict == skills_dict
    assert project.team_number == team_number
    assert project.assigned_lab == ""
    assert project.assigned_students == []
    assert project.team_capacity == 0


@given(
    name=st.text(min_size=1),
    team_number=st.integers(min_value=1, max_value=10),
    skills_dict=st.dictionaries(
        keys=st.text(min_size=1),
        values=st.integers(min_value=0, max_value=5),
        min_size=1,
    ),
)
def test_project_init_hypothesis(name: str, team_number: int, skills_dict: dict[str, int]) -> None:
    project = Project(name, team_number, skills_dict)

    assert project.name == name
    assert project.skills_dict == skills_dict
    assert project.team_number == team_number
    assert project.assigned_lab == ""
    assert project.assigned_students == []
    assert project.team_capacity == 0
