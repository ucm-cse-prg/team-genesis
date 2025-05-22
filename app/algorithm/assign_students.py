from datatypes import Student, Project, LabName
from typing import List, Dict
from pulp import (
    LpProblem,
    LpMaximize,
    LpVariable,
    lpSum,
    LpBinary,
    CPLEX_CMD,
    LpStatus,
)
import time

def assign_students(
    students: List[Student],
    projects: List[Project],
    base_team_size: int,
    pref_scalar: float = 0.5,
    optimal_gap: float = 0.01,
) -> None:
    # 1) Build safe string keys and reverse maps
    stu_keys = [s.email.replace("@", "_").replace(".", "_") for s in students]
    proj_keys = [p.name.replace(" ", "_") for p in projects]
    labs     = sorted({s.lab for s in students})
    skills   = list({skill for p in projects for skill in p.skills_dict})

    stu_map  = dict(zip(students, stu_keys))
    proj_map = dict(zip(projects, proj_keys))

    # 2) Create the PuLP model and variables
    problem = LpProblem("assign_students", LpMaximize)
    x = LpVariable.dicts("x", (stu_keys, proj_keys), cat=LpBinary)   # student→project
    y = LpVariable.dicts("y", (labs,     proj_keys), cat=LpBinary)   # lab→project
    z = LpVariable.dicts("z", (proj_keys, skills),   cat=LpBinary)   # project×skill

    # 3) Each student gets exactly one project
    for s in students:
        k = stu_map[s]
        problem += (
            lpSum(x[k][proj_map[p]] for p in projects) == 1,
            f"OneProjPerStudent_{k}"
        )

    # 4) Each project has exactly base_team_size students
    for p in projects:
        k = proj_map[p]
        problem += (
            lpSum(x[stu_map[s]][k] for s in students) == base_team_size,
            f"TeamSize_{k}"
        )

    # 5) Exactly one lab per project
    for p in projects:
        k = proj_map[p]
        problem += (
            lpSum(y[lab][k] for lab in labs) == 1,
            f"OneLabPerProject_{k}"
        )

    # 6) A student can only go to a project in their lab
    for s in students:
        sk = stu_map[s]
        for p in projects:
            pk = proj_map[p]
            problem += (
                x[sk][pk] <= y[s.lab][pk],
                f"LabMatch_{sk}_{pk}"
            )

    # 7) Build objective: weighted sum of preference and skill fulfillment
    #   7a) preference term
    total_pref = lpSum(
        x[stu_map[s]][proj_map[p]] * s.preferences[p.name]
        for s in students for p in projects
    ) / 9.0

    #   7b) skill fulfillment term
    #     a) find required skills per project
    req_sk = {p: [sk for sk, val in p.skills_dict.items() if val == 1] 
              for p in projects}
    #     b) z[p][skill] flags that at least one assigned student has skill
    for p in projects:
        pk = proj_map[p]
        for sk in req_sk[p]:
            problem += (
                lpSum(
                    x[stu_map[s]][pk] * (1 if s.skills_ratings.get(sk, 0) >= 6 else 0)
                    for s in students
                ) >= z[pk][sk],
                f"SkillFulfill_{pk}_{sk}"
            )

    total_skill = (
        lpSum(
            z[proj_map[p]][sk] * (1.0 / len(req_sk[p]))
            for p in projects for sk in req_sk[p]
        ) * 100.0 / len(projects)
    )

    problem += (
        total_pref * pref_scalar + total_skill * (1 - pref_scalar),
        "CombinedObjective"
    )

    # 8) Solve with CPLEX_CMD and keep the .lp/.sol for debugging
    solver = CPLEX_CMD(
        path="/Applications/CPLEX_Studio2211/cplex/bin/x86-64_osx/cplex",
        msg=True,
        keepFiles=1,
        timeLimit=60,
        options=[
            f"set timelimit {60}",
            f"set mip tolerances mipgap {optimal_gap}",
            f"set threads {32}",
        ],
    )
    print("Starting CPLEX…")
    start = time.time()
    status = problem.solve(solver)
    print(f"CPLEX time: {time.time() - start:.2f}s | Status: {LpStatus.get(status, status)}")
    if LpStatus.get(status) != 'Optimal':
        raise RuntimeError(f"CPLEX did not find optimal solution: {LpStatus.get(status)}")

    # 9) Extract assignments back onto Student & Project objects
    for s in students:
        sk = stu_map[s]
        for p in projects:
            pk = proj_map[p]
            val = x[sk][pk].varValue
            # skip unassigned or None values
            if val is not None and val > 0.5:
                s.assigned_project = p.name
                p.assigned_students.append(s)
                p.assigned_lab = s.lab
                p.team_capacity = base_team_size
                break
