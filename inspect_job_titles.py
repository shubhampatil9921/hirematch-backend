
import pandas as pd

cv_df = pd.read_csv("data/processed/cv_processed.csv")
job_df = pd.read_csv("data/processed/job_processed.csv")

print("\nTOP 30 CANDIDATE TARGET POSITIONS")
print("-" * 60)

print(
    cv_df["target_position"]
    .value_counts()
    .head(30)
    .to_string()
)

print("\nTOP 30 JOB TITLES")
print("-" * 60)

print(
    job_df["job_title"]
    .value_counts()
    .head(30)
    .to_string()
)

print("\nTITLES CONTAINING COMMON DEVELOPER TERMS")
print("-" * 60)

keywords = [
    "developer",
    "engineer",
    "programmer",
    "sde",
    "swe",
    "software",
    "data scientist",
    "analyst"
]

for keyword in keywords:
    candidate_matches = cv_df[
        cv_df["target_position"].str.contains(
            keyword, case=False, na=False
        )
    ]["target_position"].value_counts().head(10)

    job_matches = job_df[
        job_df["job_title"].str.contains(
            keyword, case=False, na=False
        )
    ]["job_title"].value_counts().head(10)

    print(f"\nKeyword: {keyword}")
    print("Candidate titles:")
    print(candidate_matches.to_string())

    print("Job titles:")
    print(job_matches.to_string())
