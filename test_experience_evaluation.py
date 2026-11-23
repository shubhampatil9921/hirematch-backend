
import pandas as pd

from app.ml.experience_matcher import ExperienceMatcher


# Load processed datasets
cv_df = pd.read_csv("data/processed/cv_processed.csv")
job_df = pd.read_csv("data/processed/job_processed.csv")
matches_df = pd.read_csv("data/raw/matches.csv")


# Standardize IDs before joining
cv_df["candidate_id"] = cv_df["candidate_id"].astype(str)
job_df["job_id"] = job_df["job_id"].astype(str)

matches_df["candidate_id"] = matches_df["candidate_id"].astype(str)
matches_df["job_id"] = matches_df["job_id"].astype(str)


# Keep only the required columns
candidates = cv_df[["candidate_id", "years_experience"]]
jobs = job_df[["job_id", "years_required"]]


# Join candidate and job experience information
pairs = matches_df[["candidate_id", "job_id"]].merge(
    candidates,
    on="candidate_id",
    how="left",
    validate="many_to_one"
).merge(
    jobs,
    on="job_id",
    how="left",
    validate="many_to_one"
)


# Convert experience values to numeric
pairs["years_experience"] = pd.to_numeric(
    pairs["years_experience"], errors="coerce"
)

pairs["years_required"] = pd.to_numeric(
    pairs["years_required"], errors="coerce"
)


print("Total candidate-job pairs:", len(pairs))
print("Missing candidate experience:", pairs["years_experience"].isna().sum())
print("Missing job requirements:", pairs["years_required"].isna().sum())


# Keep valid pairs for evaluation
valid_pairs = pairs.dropna(
    subset=["years_experience", "years_required"]
).copy()


# Initialize matcher
matcher = ExperienceMatcher()


# Calculate experience matching results
results = valid_pairs.apply(
    lambda row: matcher.calculate_experience_match(
        row["years_experience"],
        row["years_required"]
    ),
    axis=1
)

results_df = pd.DataFrame(results.tolist())

evaluation_df = pd.concat(
    [valid_pairs.reset_index(drop=True), results_df],
    axis=1
)


# Display evaluation statistics
print("\nEXPERIENCE MATCHING EVALUATION")
print("-" * 45)

print("Evaluated pairs:", len(evaluation_df))

print(
    "Average experience score:",
    round(evaluation_df["experience_score"].mean(), 2)
)

print(
    "Median experience score:",
    round(evaluation_df["experience_score"].median(), 2)
)

print(
    "Minimum experience score:",
    evaluation_df["experience_score"].min()
)

print(
    "Maximum experience score:",
    evaluation_df["experience_score"].max()
)

print(
    "Candidates meeting requirements:",
    evaluation_df["meets_requirement"].sum()
)

print(
    "Candidates below requirements:",
    (~evaluation_df["meets_requirement"]).sum()
)

print(
    "Percentage meeting requirements:",
    round(evaluation_df["meets_requirement"].mean() * 100, 2),
    "%"
)
