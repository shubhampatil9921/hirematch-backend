
from app.ml.esco_vocabulary import ESCOVocabulary
from app.ml.semantic_skill_matcher import SemanticSkillMatcher


vocabulary = ESCOVocabulary(
    "data/raw/esco/skills_en.csv"
)

matcher = SemanticSkillMatcher(
    threshold=0.82,
    esco_vocabulary=vocabulary
)

skill_a = "data visualization"
skill_b = "data visualisation"

# Calculate embedding similarity directly.
embeddings = matcher._get_embeddings([skill_a, skill_b])
similarity = float(embeddings[0] @ embeddings[1])

print("Semantic similarity:", round(similarity, 4))

# Test the complete matching pipeline.
result = matcher.calculate_skill_match(
    [skill_a],
    [skill_b]
)

print("\nMatching result:")
print("Matched:", result["matched_skills"])
print("Missing:", result["missing_skills"])
print("Semantic matches:", result["semantic_match_count"])
print("Coverage:", result["skill_coverage"], "%")
