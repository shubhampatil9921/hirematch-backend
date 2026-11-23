from app.ml.esco_vocabulary import ESCOVocabulary


vocabulary = ESCOVocabulary(
    "data/raw/esco/skills_en.csv"
)

pairs = [
    ("Machine Learning", "ML"),
    ("JavaScript", "JS"),
    ("Natural Language Processing", "NLP"),
    ("Artificial Intelligence", "AI"),
    ("MySQL", "SQL"),
    ("React", "ReactJS"),
    ("Python", "Java"),
    ("Data Analysis", "Data Analytics"),
    ("Deep Learning", "Neural Networks")
]

print("\nESCO vocabulary results\n")

for skill_a, skill_b in pairs:
    concept_a = vocabulary.resolve(skill_a)
    concept_b = vocabulary.resolve(skill_b)

    equivalent = vocabulary.compare(skill_a, skill_b)

    print(f"{skill_a} <-> {skill_b}")
    print("  Equivalent:", equivalent)

    print(
        "  First concept:",
        concept_a["preferred_label"] if concept_a else "Not resolved"
    )

    print(
        "  Second concept:",
        concept_b["preferred_label"] if concept_b else "Not resolved"
    )

    print()