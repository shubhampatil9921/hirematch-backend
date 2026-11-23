
import re

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.ml.title_aliases import TITLE_ALIASES


class SemanticTitleMatcher:

    def __init__(
        self,
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model=None
    ):
        # Reuse an existing model when one is supplied.
        self.model = (
            model if model is not None
            else SentenceTransformer(model_name)
        )
        self.embedding_cache = {}

    def normalize_title(self, title):
        """Normalize titles and expand standalone abbreviations."""

        if not isinstance(title, str) or not title.strip():
            raise ValueError("Title cannot be empty.")

        title = title.lower().strip()

        for abbreviation, full_form in TITLE_ALIASES.items():
            pattern = rf"\b{re.escape(abbreviation)}\b"
            title = re.sub(pattern, full_form, title)

        title = re.sub(r"[^a-z0-9\s]", " ", title)
        title = re.sub(r"\s+", " ", title)

        return title.strip()

    def get_embedding(self, title):
        """Generate and cache a semantic embedding for a title."""

        normalized_title = self.normalize_title(title)

        if normalized_title not in self.embedding_cache:
            self.embedding_cache[normalized_title] = (
                self.model.encode(
                    normalized_title,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                    show_progress_bar=False
                )
            )

        return self.embedding_cache[normalized_title]

    def calculate_title_similarity(
        self,
        candidate_title,
        job_title
    ):
        """Calculate semantic similarity between two job titles."""

        candidate_embedding = self.get_embedding(candidate_title)
        job_embedding = self.get_embedding(job_title)

        similarity = cosine_similarity(
            candidate_embedding.reshape(1, -1),
            job_embedding.reshape(1, -1)
        )[0][0]

        similarity = max(0.0, min(float(similarity), 1.0))

        return {
            "candidate_title": candidate_title,
            "job_title": job_title,
            "title_similarity": round(similarity, 4),
            "title_score": round(similarity * 100, 2)
        }
