
from app.ml.skill_aliases import SKILL_ALIASES


def normalize_skill(skill):
    return skill.lower().strip()


def resolve_alias(skill):
    normalized = normalize_skill(skill)
    return SKILL_ALIASES.get(normalized, normalized)


pairs = [
    ("Machine Learning", "ML"),
    ("JavaScript", "JS"),
    ("Artificial Intelligence", "AI"),
    ("React", "ReactJS"),
    ("Python", "Java"),
]

for first, second in pairs:
    result = resolve_alias(first) == resolve_alias(second)

    print(f"{first} <-> {second}: {result}")
