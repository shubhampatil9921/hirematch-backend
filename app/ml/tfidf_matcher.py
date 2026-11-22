
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TfidfMatcher:

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=10000
        )

    def calculate_similarity(self, resume_text, job_text):

        if not resume_text or not job_text:
            raise ValueError("Resume text and job text cannot be empty.")

        documents = [resume_text, job_text]

        tfidf_matrix = self.vectorizer.fit_transform(documents)

        similarity = cosine_similarity(
            tfidf_matrix[0:1],
            tfidf_matrix[1:2]
        )[0][0]

        return round(float(similarity), 4)
