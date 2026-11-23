
import pandas as pd

cv_df = pd.read_csv("data/processed/cv_processed.csv")
job_df = pd.read_csv("data/processed/job_processed.csv")
matches_df = pd.read_csv("data/raw/matches.csv")

cv_df["candidate_id"] = cv_df["candidate_id"].astype(str)
job_df["job_id"] = job_df["job_id"].astype(str)

matches_df["candidate_id"] = matches_df["candidate_id"].astype(str)
matches_df["job_id"] = matches_df["job_id"].astype(str)

pairs = matches_df[
    ["candidate_id", "job_id"]
].merge(
    cv_df[["candidate_id", "target_position"]],
    on="candidate_id"
).merge(
    job_df[["job_id", "job_title"]],
    on="job_id"
)

print("TOTAL TITLE COMBINATIONS:", len(pairs))

print("\nRANDOM 30 CANDIDATE-JOB TITLE PAIRS")
print("-" * 80)

sample = pairs.sample(n=30, random_state=42)

for _, row in sample.iterrows():
    print(f"Candidate: {row['target_position']}")
    print(f"Job:       {row['job_title']}")
    print("-" * 60)
