
class MatchingService:
    """
    Coordinate all HireMatch matching components and calculate
    a transparent weighted compatibility score.
    """

    DEFAULT_WEIGHTS = {
        "skills": 0.40,
        "resume_text": 0.25,
        "experience": 0.15,
        "title": 0.15,
        "category": 0.05,
    }

    def __init__(
        self,
        tfidf_matcher,
        skill_matcher,
        experience_matcher,
        category_matcher,
        title_matcher,
        weights=None,
    ):
        self.tfidf_matcher = tfidf_matcher
        self.skill_matcher = skill_matcher
        self.experience_matcher = experience_matcher
        self.category_matcher = category_matcher
        self.title_matcher = title_matcher

        self.weights = weights or self.DEFAULT_WEIGHTS.copy()

        if set(self.weights) != set(self.DEFAULT_WEIGHTS):
            raise ValueError("Weights must contain all five score components.")

        if any(
            not isinstance(weight, (int, float)) or weight < 0
            for weight in self.weights.values()
        ):
            raise ValueError("Weights must be non-negative numbers.")

        if sum(self.weights.values()) <= 0:
            raise ValueError("At least one weight must be greater than zero.")

        # Normalize weights so they always add up to 1.
        total_weight = sum(self.weights.values())
        self.weights = {
            name: weight / total_weight
            for name, weight in self.weights.items()
        }

    def calculate_match(
        self,
        resume_text,
        job_text,
        resume_skills,
        job_skills,
        candidate_experience,
        required_experience,
        candidate_category,
        job_category,
        candidate_title,
        job_title,
    ):
        """Calculate all component scores and the overall match score."""

        # 1. Resume and job-description text similarity.
        text_similarity = self.tfidf_matcher.calculate_similarity(
            resume_text,
            job_text
        )

        # 2. Required skill coverage, including semantic matches.
        skill_result = self.skill_matcher.calculate_skill_match(
            resume_skills,
            job_skills
        )

        # 3. Experience compatibility.
        experience_result = (
            self.experience_matcher.calculate_experience_match(
                candidate_experience,
                required_experience
            )
        )

        # 4. Category alignment.
        category_result = self.category_matcher.calculate_category_match(
            candidate_category,
            job_category
        )

        # 5. Semantic job-title similarity.
        title_result = self.title_matcher.calculate_title_similarity(
            candidate_title,
            job_title
        )

        # Convert component values to a common 0-100 scale.
        component_scores = {
            "skills": skill_result["skill_coverage"],
            "resume_text": text_similarity * 100,
            "experience": experience_result["experience_score"],
            "title": title_result["title_score"],
            "category": category_result["category_score"],
        }

        overall_score = sum(
            component_scores[name] * self.weights[name]
            for name in self.weights
        )

        return {
            "overall_score": round(overall_score, 2),
            "score_breakdown": {
                name: {
                    "score": round(component_scores[name], 2),
                    "weight": round(self.weights[name] * 100, 2),
                    "weighted_score": round(
                        component_scores[name] * self.weights[name],
                        2
                    ),
                }
                for name in self.weights
            },
            "text_similarity": round(text_similarity, 4),
            "skill_match": skill_result,
            "experience_match": experience_result,
            "category_match": category_result,
            "title_match": title_result,
            "score_interpretation": (
                "A weighted compatibility score based on the supplied "
                "resume and job information. It is not a probability "
                "of being hired."
            ),
        }
