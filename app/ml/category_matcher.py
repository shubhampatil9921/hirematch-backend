
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class CategoryMatcher:

    def normalize_text(self, text):
        """Normalize category and job title text."""

        if not isinstance(text, str):
            return ""

        text = text.lower().strip()

        # Expand abbreviations and preserve word boundaries.
        text = re.sub(r"\bsr\.?\s*", "senior ", text)
        text = re.sub(r"\bjr\.?\s*", "junior ", text)
        text = re.sub(r"\basst\.?\s*", "assistant ", text)

        # Remove parenthesized text only when it is a short abbreviation.
        text = re.sub(
            r"\s*\(([a-z]{1,5})\)",
            "",
            text
        )

        # Standardize punctuation and whitespace.
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def calculate_category_match(
        self,
        candidate_category,
        job_category
    ):
        """Compare candidate and job categories."""

        candidate = self.normalize_text(candidate_category)
        job = self.normalize_text(job_category)

        if not candidate or not job:
            raise ValueError("Category values cannot be empty.")

        is_match = candidate == job

        return {
            "candidate_category": candidate,
            "job_category": job,
            "category_match": is_match,
            "category_score": 100.0 if is_match else 0.0
        }

    def calculate_title_similarity(
        self,
        candidate_title,
        job_title
    ):
        """Calculate TF-IDF cosine similarity between job titles."""

        candidate = self.normalize_text(candidate_title)
        job = self.normalize_text(job_title)

        if not candidate or not job:
            raise ValueError("Title values cannot be empty.")

        if candidate == job:
            similarity = 1.0
        else:
            vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2)
            )

            tfidf_matrix = vectorizer.fit_transform(
                [candidate, job]
            )

            similarity = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2]
            )[0][0]

        return {
            "candidate_title": candidate,
            "job_title": job,
            "title_similarity": round(float(similarity), 4),
            "title_score": round(float(similarity) * 100, 2)
        }
