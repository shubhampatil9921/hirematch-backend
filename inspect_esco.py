import pandas as pd
from pathlib import Path

ESCO_FILE = Path("data/raw/esco/skills_en.csv")

esco_df = pd.read_csv(
    ESCO_FILE,
    encoding="utf-8",
    low_memory=False
)

print("Dataset shape:", esco_df.shape)

print("\nColumns:")
print(esco_df.columns.tolist())

print("\nMissing values:")
print(
    esco_df[
        ["conceptUri", "preferredLabel", "altLabels", "hiddenLabels"]
    ].isna().sum()
)

print("\nFirst 5 skill records:")

print(
    esco_df[
        ["preferredLabel", "altLabels", "hiddenLabels"]
    ].head().to_string(index=False)
)

# Inspect specific terms and abbreviations.
search_terms = [
    "machine learning",
    "ML",
    "javascript",
    "JS",
    "natural language processing",
    "NLP",
    "artificial intelligence",
    "AI",
    "MySQL",
    "SQL",
    "React"
]

print("\nTarget skill search:")

for term in search_terms:
    mask = (
        esco_df["preferredLabel"].str.contains(
            term, case=False, na=False
        )
        | esco_df["altLabels"].str.contains(
            term, case=False, na=False
        )
        | esco_df["hiddenLabels"].str.contains(
            term, case=False, na=False
        )
    )

    results = esco_df.loc[
        mask,
        ["preferredLabel", "altLabels", "hiddenLabels"]
    ].head(5)

    print(f"\n--- {term} ---")

    if results.empty:
        print("No matching records found.")
    else:
        print(results.to_string(index=False))