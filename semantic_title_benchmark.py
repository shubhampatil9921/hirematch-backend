
from app.ml.semantic_title_matcher import SemanticTitleMatcher


matcher = SemanticTitleMatcher()

test_pairs = [
    ("Software Engineer", "Software Developer"),
    ("SDE", "Software Development Engineer"),
    ("Machine Learning Engineer", "Data Scientist"),
    ("Database Administrator", "Information Technology Administrator"),
    ("Civil Engineer", "Finance Manager"),
]

print("\nSEMANTIC TITLE MATCHING RESULTS")
print("-" * 70)

for candidate_title, job_title in test_pairs:

    result = matcher.calculate_title_similarity(
        candidate_title,
        job_title
    )

    print(f"Candidate: {result['candidate_title']}")
    print(f"Job:       {result['job_title']}")
    print(f"Similarity: {result['title_similarity']}")
    print(f"Score:      {result['title_score']}%")
    print("-" * 70)
