
from app.ml.tfidf_matcher import TfidfMatcher


matcher = TfidfMatcher()

resume = """
Python developer with experience in machine learning,
data analysis, SQL, pandas, NumPy and scikit-learn.
Built machine learning models and data processing applications.
"""

job = """
We are looking for a Python developer with experience in
machine learning, SQL, data analysis and scikit-learn.
Knowledge of pandas and NumPy is preferred.
"""

score = matcher.calculate_similarity(resume, job)

print("TF-IDF Similarity Score:", score)
print("Similarity Percentage:", score * 100, "%")


unrelated_job = """
We need a sales manager with experience in negotiation,
customer relationships, business development and marketing.
"""

unrelated_score = matcher.calculate_similarity(
    resume,
    unrelated_job
)

print("Unrelated Job Similarity:", unrelated_score)

try:
    matcher.calculate_similarity("", job)
except ValueError as error:
    print("Empty input test passed:", error)
