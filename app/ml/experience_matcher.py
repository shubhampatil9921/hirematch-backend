
class ExperienceMatcher:

    def calculate_experience_match(
        self,
        candidate_experience,
        required_experience
    ):
        """
        Compare candidate experience with job requirements.
        """

        if candidate_experience is None:
            raise ValueError("Candidate experience cannot be None.")

        if required_experience is None:
            raise ValueError("Required experience cannot be None.")

        if candidate_experience < 0:
            raise ValueError("Candidate experience cannot be negative.")

        if required_experience < 0:
            raise ValueError("Required experience cannot be negative.")

        if candidate_experience >= required_experience:
            meets_requirement = True
            experience_gap = 0
        else:
            meets_requirement = False
            experience_gap = (
                required_experience - candidate_experience
            )

        if required_experience == 0:
            experience_score = 100.0
        else:
            experience_score = min(
                (candidate_experience / required_experience) * 100,
                100.0
            )

        return {
            "candidate_experience": candidate_experience,
            "required_experience": required_experience,
            "meets_requirement": meets_requirement,
            "experience_gap": round(experience_gap, 2),
            "experience_score": round(experience_score, 2)
        }
