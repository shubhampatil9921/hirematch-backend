from app.ml.semantic_skill_matcher import SemanticSkillMatcher

matcher = SemanticSkillMatcher(threshold=0.82)

result = matcher.calculate_skill_match(
    resume_skills=[
        "Python",
        "Machine Learning",
        "JavaScript",
        "MySQL"
    ],
    job_skills=[
        "python",
        "ML",
        "JS",
        "SQL",
        "React"
    ]
)

print("\nSemantic matching results:")
print(result)