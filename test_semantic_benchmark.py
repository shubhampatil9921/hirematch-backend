from app.ml.esco_vocabulary import ESCOVocabulary
from app.ml.semantic_skill_matcher import SemanticSkillMatcher

vocabulary = ESCOVocabulary("data/raw/esco/skills_en.csv")

matcher = SemanticSkillMatcher(
    threshold=0.65,
    esco_vocabulary=vocabulary
)

test_pairs = [
    # Equivalent skills
    ("data visualisation", "data visualization", "equivalent"),
    ("web development", "web programming", "equivalent"),
    ("natural language processing", "NLP", "equivalent"),

    # Related but not equivalent
    ("data analysis", "data analytics", "related"),
    ("machine learning", "deep learning", "related"),
    ("database management", "data analysis", "related"),

    # Unrelated skills
    ("python programming", "financial accounting", "unrelated"),
    ("graphic design", "network security", "unrelated"),
    ("sales management", "machine learning", "unrelated"),
]

print("SEMANTIC SKILL BENCHMARK")
print("-" * 65)

for skill_a, skill_b, expected in test_pairs:
    embeddings = matcher._get_embeddings([skill_a, skill_b])
    similarity = float(embeddings[0] @ embeddings[1])

    result = matcher.calculate_skill_match(
        [skill_a],
        [skill_b]
    )

    predicted = (
        "matched"
        if result["semantic_match_count"] == 1
        else "not matched"
    )

    print(f"\nSkill A:   {skill_a}")
    print(f"Skill B:   {skill_b}")
    print(f"Expected:  {expected}")
    print(f"Similarity: {similarity:.4f}")
    print(f"Predicted: {predicted}")