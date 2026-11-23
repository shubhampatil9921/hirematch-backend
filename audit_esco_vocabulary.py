
from app.ml.esco_vocabulary import ESCOVocabulary


vocabulary = ESCOVocabulary(
    "data/raw/esco/skills_en.csv"
)

print("\nESCO VOCABULARY AUDIT")
print("=" * 55)

# 1. Overall vocabulary statistics
total_concepts = len(vocabulary.concepts)
total_labels = len(vocabulary.alias_to_concepts)

ambiguous_labels = {
    label: concepts
    for label, concepts in vocabulary.alias_to_concepts.items()
    if len(concepts) > 1
}

print(f"\nUnique concepts: {total_concepts}")
print(f"Unique normalized labels: {total_labels}")
print(f"Ambiguous labels: {len(ambiguous_labels)}")

# 2. Inspect selected skill labels
skills_to_inspect = [
    "data analysis",
    "statistics",
    "data analytics",
    "machine learning",
    "ml",
    "javascript",
    "js",
    "natural language processing",
    "nlp",
    "artificial intelligence",
    "ai",
    "react",
    "reactjs",
]

print("\nSELECTED LABEL INSPECTION")
print("=" * 55)

for skill in skills_to_inspect:
    normalized = vocabulary.normalize_label(skill)
    matches = vocabulary.alias_to_concepts.get(normalized, {})

    print(f"\nLabel: {skill}")
    print(f"Concept count: {len(matches)}")

    if not matches:
        print("  Not found")
        continue

    for uri, sources in matches.items():
        concept = vocabulary.concepts[uri]

        print(f"  Preferred label: {concept['preferred_label']}")
        print(f"  URI: {uri}")
        print(f"  Label source: {sorted(sources)}")

# 3. Show a sample of ambiguous labels
print("\nAMBIGUOUS LABEL EXAMPLES")
print("=" * 55)

for label, concepts in list(ambiguous_labels.items())[:20]:
    print(f"\nLabel: {label}")

    for uri, sources in concepts.items():
        concept = vocabulary.concepts[uri]

        print(
            f"  - {concept['preferred_label']} "
            f"({', '.join(sorted(sources))})"
        )
