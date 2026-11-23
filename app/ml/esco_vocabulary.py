import re
from collections import defaultdict
from pathlib import Path

import pandas as pd


class ESCOVocabulary:
    """
    Load ESCO skills and resolve preferred labels, alternative labels,
    and hidden labels to their standardized skill concepts.
    """

    def __init__(self, csv_path):
        self.csv_path = Path(csv_path)

        self.alias_to_concepts = defaultdict(
            lambda: defaultdict(set)
        )

        self.concepts = {}

        self._load_vocabulary()

    @staticmethod
    def normalize_label(label):
        if not isinstance(label, str):
            return ""

        label = label.casefold().strip()
        label = re.sub(r"\s+", " ", label)

        return label

    def _load_vocabulary(self):
        df = pd.read_csv(
            self.csv_path,
            encoding="utf-8",
            low_memory=False
        )

        required_columns = [
            "conceptUri",
            "preferredLabel",
            "altLabels",
            "hiddenLabels"
        ]

        missing = [
            column for column in required_columns
            if column not in df.columns
        ]

        if missing:
            raise ValueError(
                f"Missing ESCO columns: {missing}"
            )

        for _, row in df.iterrows():
            uri = row["conceptUri"]
            preferred = row["preferredLabel"]

            if not isinstance(uri, str) or not isinstance(preferred, str):
                continue

            self.concepts[uri] = {
                "uri": uri,
                "preferred_label": preferred
            }

            labels = {
                "preferred": [preferred],
                "alternative": (
                    row["altLabels"].splitlines()
                    if isinstance(row["altLabels"], str)
                    else []
                )
            }

            for source, values in labels.items():
                for label in values:
                    normalized = self.normalize_label(label)

                    if normalized:
                        self.alias_to_concepts[normalized][uri].add(
                            source
                        )


    def resolve(self, skill):
        """
        Resolve a skill only when it exactly matches one
        ESCO preferred label.

        Alternative and hidden labels are not automatically
        accepted as equivalent skills.
        """

        normalized = self.normalize_label(skill)

        if not normalized:
            return None

        matches = self.alias_to_concepts.get(normalized, {})

        # Reject ambiguous labels.
        if len(matches) != 1:
            return None

        uri, sources = next(iter(matches.items()))

        # Accept preferred labels only.
        if "preferred" not in sources:
            return None

        return {
            **self.concepts[uri],
            "matched_label": skill,
            "label_sources": sorted(sources)
        }

    def compare(self, skill_a, skill_b):
        """
        Check whether two labels resolve to the same ESCO concept.
        """

        concept_a = self.resolve(skill_a)
        concept_b = self.resolve(skill_b)

        if concept_a is None or concept_b is None:
            return False

        return concept_a["uri"] == concept_b["uri"]