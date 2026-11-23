
from app.services.matching_service import MatchingService


class FakeTfidfMatcher:
    def calculate_similarity(self, resume_text, job_text):
        return 0.5


class FakeSkillMatcher:
    def calculate_skill_match(self, resume_skills, job_skills):
        return {
            "skill_coverage": 80.0,
            "matched_skills": ["Python", "SQL"],
            "missing_skills": ["Docker"],
            "matched_count": 2,
            "missing_count": 1,
            "total_required_skills": 3,
        }


class FakeExperienceMatcher:
    def calculate_experience_match(self, candidate, required):
        return {
            "experience_score": 100.0,
            "meets_requirement": True,
            "experience_gap": 0,
        }


class FakeCategoryMatcher:
    def calculate_category_match(self, candidate, job):
        return {
            "category_match": True,
            "category_score": 100.0,
        }


class FakeTitleMatcher:
    def calculate_title_similarity(self, candidate, job):
        return {
            "title_similarity": 0.9,
            "title_score": 90.0,
        }


def create_service():
    return MatchingService(
        tfidf_matcher=FakeTfidfMatcher(),
        skill_matcher=FakeSkillMatcher(),
        experience_matcher=FakeExperienceMatcher(),
        category_matcher=FakeCategoryMatcher(),
        title_matcher=FakeTitleMatcher(),
    )


def test_matching_service_returns_all_components():
    service = create_service()

    result = service.calculate_match(
        resume_text="Python developer with SQL experience",
        job_text="Python developer required with SQL and Docker",
        resume_skills=["Python", "SQL"],
        job_skills=["Python", "SQL", "Docker"],
        candidate_experience=4,
        required_experience=3,
        candidate_category="INFORMATION-TECHNOLOGY",
        job_category="INFORMATION-TECHNOLOGY",
        candidate_title="Software Engineer",
        job_title="Software Developer",
    )

    assert result["overall_score"] == 78.0
    assert result["skill_match"]["skill_coverage"] == 80.0
    assert result["experience_match"]["meets_requirement"] is True
    assert result["category_match"]["category_match"] is True
    assert result["title_match"]["title_score"] == 90.0


def test_weights_are_normalized():
    service = create_service()

    assert sum(service.weights.values()) == 1.0


def test_invalid_weights_are_rejected():
    try:
        MatchingService(
            tfidf_matcher=FakeTfidfMatcher(),
            skill_matcher=FakeSkillMatcher(),
            experience_matcher=FakeExperienceMatcher(),
            category_matcher=FakeCategoryMatcher(),
            title_matcher=FakeTitleMatcher(),
            weights={
                "skills": -1,
                "resume_text": 1,
                "experience": 1,
                "title": 1,
                "category": 1,
            },
        )
    except ValueError as error:
        assert "non-negative" in str(error)
    else:
        raise AssertionError("Invalid weights should raise ValueError.")

