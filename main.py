from form_teams import form_teams

# import pymongo  # type: ignore
# import certifi
# from uri import URI  # type: ignore

if __name__ == "__main__":
    # print("Pinging database...")
    # client = pymongo.MongoClient(URI, tlsCAFile=certifi.where())
    # try:
    #     client.admin.command("ping")
    #     print("Ping Successful")
    # except Exception as e:
    #     print(f"Connection failed\n{e}")

    SEED = 42
    # form_teams(
    #     "student_data/2024-01-Spring-CSE-MASTER.xlsx",
    #     "student_data/student_skills.json",
    #     "student_data/PROJECT_SKILLS_S2024.json",
    #     5,
    #     "student_data/SKILLS_LIST_2024.txt",
    #     # client,
    #     formed_teams_filename="output/formed_teams.csv",
    #     team_pref_scores_filename="output/team_pref_scores.csv",
    #     histogram_filename="output/metrics_per_team_histogram_labless.png",
    #     option=3,
    #     seed=SEED,
    # )
    form_teams(
        "student_data/2025-01-Spring-CSE-MASTER.xlsx",
        # "student_data/survey_results.csv",
        # "PROJECT_SKILLS_S2024.json",
        5,
        "student_data/SKILLS_LIST_S25.txt",
        # client,
        formed_teams_filename="output/formed_teams.csv",
        team_pref_scores_filename="output/team_pref_scores.csv",
        histogram_filename="output/metrics_per_team_histogram_with_labs.png",
        option=2,
        seed=SEED,
    )
