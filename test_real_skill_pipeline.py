
from app.ml.esco_vocabulary import ESCOVocabulary
from app.ml.semantic_skill_matcher import SemanticSkillMatcher


vocabulary = ESCOVocabulary(
    "data/raw/esco/skills_en.csv"
)

matcher = SemanticSkillMatcher(
    threshold=0.82,
    esco_vocabulary=vocabulary
)

test_cases = [
    {
        "name": "Manual alias",
        "resume": ["ML"],
        "job": ["Machine Learning"]
    },
    {
        "name": "ESCO preferred label",
        "resume": ["Python"],
        "job": ["Python"]
    },
    {
        "name": "Manual NLP alias",
        "resume": ["NLP"],
        "job": ["Natural Language Processing"]
    },
    {
        "name": "Unrelated skills",
        "resume": ["Python"],
        "job": ["Accounting"]
    },
    {
        "name": "Related but different skills",
        "resume": ["Data Analysis"],
        "job": ["Data Analytics"]
    }
]

for case in test_cases:
    result = matcher.calculate_skill_match(
        case["resume"],
        case["job"]
    )

    print(f"\n{case['name']}")
    print("Matched:", result["matched_skills"])
    print("Missing:", result["missing_skills"])
    print("Exact/alias matches:", result["exact_match_count"])
    print("Semantic matches:", result["semantic_match_count"])
    print("Coverage:", result["skill_coverage"], "%")
