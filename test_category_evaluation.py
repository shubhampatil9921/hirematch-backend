
import pandas as pd

from app.ml.category_matcher import CategoryMatcher


# Load processed datasets
cv_df = pd.read_csv("data/processed/cv_processed.csv")
job_df = pd.read_csv("data/processed/job_processed.csv")
matches_df = pd.read_csv("data/raw/matches.csv")


# Standardize IDs
cv_df["candidate_id"] = cv_df["candidate_id"].astype(str)
job_df["job_id"] = job_df["job_id"].astype(str)

matches_df["candidate_id"] = matches_df["candidate_id"].astype(str)
matches_df["job_id"] = matches_df["job_id"].astype(str)


# Select required columns
candidates = cv_df[
    ["candidate_id", "inferred_category", "target_position"]
]

jobs = job_df[
    ["job_id", "category", "job_title"]
]


# Join candidate and job data
pairs = matches_df[
    ["candidate_id", "job_id"]
].merge(
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


print("Total candidate-job pairs:", len(pairs))
print("Missing candidate categories:", pairs["inferred_category"].isna().sum())
print("Missing job categories:", pairs["category"].isna().sum())
print("Missing candidate titles:", pairs["target_position"].isna().sum())
print("Missing job titles:", pairs["job_title"].isna().sum())


# Initialize matcher
matcher = CategoryMatcher()


# Remove rows with missing values for this evaluation
valid_pairs = pairs.dropna(
    subset=[
        "inferred_category",
        "category",
        "target_position",
        "job_title"
    ]
).copy()


# Calculate category and title scores
category_results = valid_pairs.apply(
    lambda row: matcher.calculate_category_match(
        row["inferred_category"],
        row["category"]
    ),
    axis=1
)

title_results = valid_pairs.apply(
    lambda row: matcher.calculate_title_similarity(
        row["target_position"],
        row["job_title"]
    ),
    axis=1
)


category_df = pd.DataFrame(category_results.tolist())
title_df = pd.DataFrame(title_results.tolist())

evaluation_df = pd.concat(
    [
        valid_pairs.reset_index(drop=True),
        category_df.reset_index(drop=True),
        title_df.reset_index(drop=True)
    ],
    axis=1
)


# Display results
print("\nCATEGORY MATCHING EVALUATION")
print("-" * 45)

print("Evaluated pairs:", len(evaluation_df))

print(
    "Category match count:",
    evaluation_df["category_match"].sum()
)

print(
    "Category mismatch count:",
    (~evaluation_df["category_match"]).sum()
)

print(
    "Category match percentage:",
    round(evaluation_df["category_match"].mean() * 100, 2),
    "%"
)

print(
    "\nAverage title similarity:",
    round(evaluation_df["title_similarity"].mean(), 4)
)

print(
    "Median title similarity:",
    round(evaluation_df["title_similarity"].median(), 4)
)

print(
    "Minimum title similarity:",
    evaluation_df["title_similarity"].min()
)

print(
    "Maximum title similarity:",
    evaluation_df["title_similarity"].max()
)


# Show sample comparisons
print("\nSAMPLE COMPARISONS")
print("-" * 45)

print(
    evaluation_df[
        [
            "inferred_category",
            "category",
            "target_position",
            "job_title",
            "category_score",
            "title_score"
        ]
    ].head(10).to_string(index=False)
)
