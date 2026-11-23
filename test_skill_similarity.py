from app.ml.semantic_skill_matcher import SemanticSkillMatcher

matcher = SemanticSkillMatcher(threshold=0.0)

pairs = [
    ("Machine Learning", "ML"),
    ("JavaScript", "JS"),
    ("Natural Language Processing", "NLP"),
    ("Artificial Intelligence", "AI"),
    ("MySQL", "SQL"),
    ("React", "ReactJS"),
    ("Python", "Java"),
    ("Data Analysis", "Data Analytics"),
    ("Deep Learning", "Neural Networks"),
]

for resume_skill, job_skill in pairs:
    embeddings = matcher._get_embeddings([
        matcher.normalize_skill(resume_skill),
        matcher.normalize_skill(job_skill)
    ])

    similarity = float(embeddings[0] @ embeddings[1])

    print(
        f"{resume_skill:30} | "
        f"{job_skill:25} | "
        f"{similarity:.4f}"
    )