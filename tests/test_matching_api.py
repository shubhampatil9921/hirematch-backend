
from fastapi.testclient import TestClient

from app.main import create_app
from app.core.resources import AppResources


class FakeMatchingService:
    def calculate_match(self, **kwargs):
        return {
            "overall_score": 78.0,
            "score_breakdown": {
                "skills": {
                    "score": 80.0,
                    "weight": 40.0,
                    "weighted_score": 32.0,
                },
                "resume_text": {
                    "score": 50.0,
                    "weight": 25.0,
                    "weighted_score": 12.5,
                },
                "experience": {
                    "score": 100.0,
                    "weight": 15.0,
                    "weighted_score": 15.0,
                },
                "title": {
                    "score": 90.0,
                    "weight": 15.0,
                    "weighted_score": 13.5,
                },
                "category": {
                    "score": 100.0,
                    "weight": 5.0,
                    "weighted_score": 5.0,
                },
            },
            "text_similarity": 0.5,
            "skill_match": {
                "exact_matched_skills": ["Python", "SQL"],
                "semantic_matched_skills": [],
                "matched_skills": ["Python", "SQL"],
                "missing_skills": ["Docker"],
                "total_required_skills": 3,
                "exact_match_count": 2,
                "semantic_match_count": 0,
                "matched_count": 2,
                "missing_count": 1,
                "skill_coverage": 80.0,
            },
            "experience_match": {
                "candidate_experience": 4.0,
                "required_experience": 3.0,
                "meets_requirement": True,
                "experience_gap": 0.0,
                "experience_score": 100.0,
            },
            "category_match": {
                "candidate_category": "information technology",
                "job_category": "information technology",
                "category_match": True,
                "category_score": 100.0,
            },
            "title_match": {
                "candidate_title": "Software Engineer",
                "job_title": "Software Developer",
                "title_similarity": 0.9,
                "title_score": 90.0,
            },
            "score_interpretation": (
                "A weighted compatibility score. "
                "It is not a probability of being hired."
            ),
        }


class FakeResources:
    def __init__(self):
        self.matching_service = FakeMatchingService()


def fake_resource_factory():
    return FakeResources()


def valid_payload():
    return {
        "resume_text": "Python developer with SQL experience.",
        "job_text": "Python developer required with SQL and Docker.",
        "resume_skills": ["Python", "SQL"],
        "job_skills": ["Python", "SQL", "Docker"],
        "candidate_experience": 4,
        "required_experience": 3,
        "candidate_category": "INFORMATION-TECHNOLOGY",
        "job_category": "INFORMATION-TECHNOLOGY",
        "candidate_title": "Software Engineer",
        "job_title": "Software Developer",
    }


def test_matching_endpoint_returns_success():
    app = create_app(resource_factory=fake_resource_factory)

    with TestClient(app) as client:
        response = client.post(
            "/api/match",
            json=valid_payload(),
        )

    assert response.status_code == 200
    assert response.json()["overall_score"] == 78.0


def test_matching_endpoint_rejects_negative_experience():
    app = create_app(resource_factory=fake_resource_factory)

    payload = valid_payload()
    payload["candidate_experience"] = -1

    with TestClient(app) as client:
        response = client.post("/api/match", json=payload)

    assert response.status_code == 422


def test_matching_endpoint_rejects_missing_fields():
    app = create_app(resource_factory=fake_resource_factory)

    payload = valid_payload()
    del payload["resume_text"]

    with TestClient(app) as client:
        response = client.post("/api/match", json=payload)

    assert response.status_code == 422


def test_matching_endpoint_rejects_empty_resume():
    app = create_app(resource_factory=fake_resource_factory)

    payload = valid_payload()
    payload["resume_text"] = ""

    with TestClient(app) as client:
        response = client.post("/api/match", json=payload)

    assert response.status_code == 422
