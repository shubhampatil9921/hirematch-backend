
import pymupdf
from fastapi.testclient import TestClient

from app.main import create_app

class FakeMatchingService:
    def calculate_match(self, **kwargs):
        return {
            "overall_score": 75.0,
            "score_breakdown": {},
            "text_similarity": 0.5,
            "skill_match": {},
            "experience_match": {},
            "category_match": {},
            "title_match": {},
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

def create_test_pdf():
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text(
        (72, 72),
        "Python Developer with SQL experience."
    )

    pdf_bytes = document.tobytes()
    document.close()

    return pdf_bytes

def test_resume_extract_endpoint():
    app = create_app(resource_factory=fake_resource_factory)

    with TestClient(app) as client:
        response = client.post(
            "/api/resume/extract",
            files={
                "file": (
                    "resume.pdf",
                    create_test_pdf(),
                    "application/pdf",
                )
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "resume.pdf"
    assert "Python Developer" in data["extracted_text"]
    assert data["page_count"] == 1

def test_resume_endpoint_rejects_non_pdf():
    app = create_app(resource_factory=fake_resource_factory)

    with TestClient(app) as client:
        response = client.post(
            "/api/resume/extract",
            files={
                "file": (
                    "resume.txt",
                    b"Some resume text",
                    "text/plain",
                )
            },
        )

    assert response.status_code == 415

def test_resume_endpoint_rejects_large_file():
    app = create_app(resource_factory=fake_resource_factory)

    with TestClient(app) as client:
        response = client.post(
            "/api/resume/extract",
            files={
                "file": (
                    "large.pdf",
                    b"x" * (5 * 1024 * 1024 + 1),
                    "application/pdf",
                )
            },
        )

    assert response.status_code == 413



def create_analysis_pdf():
    document = pymupdf.open()
    page = document.new_page()

    page.insert_textbox(
        (50, 50, 550, 300),
        (
            "John Doe\n"
            "Software Engineer\n"
            "Python, SQL, React and Docker\n"
            "4 years of experience"
        ),
    )

    pdf_bytes = document.tobytes()
    document.close()

    return pdf_bytes

def create_custom_pdf(text):
    document = pymupdf.open()
    page = document.new_page()

    page.insert_textbox(
        (50, 50, 550, 500),
        text,
    )

    pdf_bytes = document.tobytes()
    document.close()

    return pdf_bytes


def submit_resume_match(
    client,
    pdf_bytes,
    job_skills='["Python", "React", "SQL"]',
    candidate_experience=None,
    candidate_title=None,
):
    data = {
        "job_text": (
            "We need a Software Developer experienced in "
            "Python, React and SQL."
        ),
        "job_skills": job_skills,
        "job_title": "Software Developer",
        "job_category": "INFORMATION-TECHNOLOGY",
        "required_experience": "2",
        "candidate_category": "INFORMATION-TECHNOLOGY",
    }

    if candidate_experience is not None:
        data["candidate_experience"] = str(candidate_experience)

    if candidate_title is not None:
        data["candidate_title"] = candidate_title

    return client.post(
        "/api/resume/match",
        data=data,
        files={
            "file": (
                "resume.pdf",
                pdf_bytes,
                "application/pdf",
            )
        },
    )

def test_resume_analyze_endpoint():
    app = create_app(resource_factory=fake_resource_factory)

    with TestClient(app) as client:
        response = client.post(
            "/api/resume/analyze",
            files={
                "file": (
                    "resume.pdf",
                    create_analysis_pdf(),
                    "application/pdf",
                )
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "resume.pdf"
    assert "Python" in data["skills"]
    assert "SQL" in data["skills"]
    assert "React" in data["skills"]
    assert data["years_experience"] == 4.0
    assert data["candidate_title"] == "Software Engineer"


def test_resume_analyze_endpoint_rejects_non_pdf():
    app = create_app(resource_factory=fake_resource_factory)

    with TestClient(app) as client:
        response = client.post(
            "/api/resume/analyze",
            files={
                "file": (
                    "resume.txt",
                    b"Some resume text",
                    "text/plain",
                )
            },
        )

    assert response.status_code == 415

def test_resume_match_endpoint_with_json_skills():
    app = create_app(resource_factory=fake_resource_factory)

    with TestClient(app) as client:
        response = submit_resume_match(
            client,
            create_analysis_pdf(),
            job_skills='["Python", "React", "SQL"]',
        )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "resume.pdf"
    assert "resume_analysis" in data
    assert "match_result" in data

    assert data["match_result"]["overall_score"] == 75.0
    assert data["resume_analysis"]["candidate_title"] == "Software Engineer"


def test_resume_match_endpoint_with_comma_separated_skills():
    app = create_app(resource_factory=fake_resource_factory)

    with TestClient(app) as client:
        response = submit_resume_match(
            client,
            create_analysis_pdf(),
            job_skills="Python,React,SQL",
        )

    assert response.status_code == 200

    data = response.json()

    assert data["match_result"]["overall_score"] == 75.0

def test_resume_match_rejects_invalid_json_skills():
    app = create_app(resource_factory=fake_resource_factory)

    with TestClient(app) as client:
        response = submit_resume_match(
            client,
            create_analysis_pdf(),
            job_skills='["Python", "React"',
        )

    assert response.status_code == 422


def test_resume_match_rejects_empty_skills():
    app = create_app(resource_factory=fake_resource_factory)

    with TestClient(app) as client:
        response = submit_resume_match(
            client,
            create_analysis_pdf(),
            job_skills="[]",
        )

    assert response.status_code == 422

def test_resume_match_rejects_missing_candidate_experience():
    app = create_app(resource_factory=fake_resource_factory)

    pdf = create_custom_pdf(
        "John Doe\n"
        "Software Engineer\n"
        "Python, React and SQL"
    )

    with TestClient(app) as client:
        response = submit_resume_match(
            client,
            pdf,
        )

    assert response.status_code == 422
    assert "experience" in response.json()["detail"].lower()


def test_resume_match_rejects_missing_candidate_title():
    app = create_app(resource_factory=fake_resource_factory)

    pdf = create_custom_pdf(
        "John Doe\n"
        "Python, React and SQL\n"
        "4 years of experience"
    )

    with TestClient(app) as client:
        response = submit_resume_match(
            client,
            pdf,
        )

    assert response.status_code == 422
    assert "title" in response.json()["detail"].lower()

def test_resume_match_rejects_non_pdf():
    app = create_app(resource_factory=fake_resource_factory)

    with TestClient(app) as client:
        response = client.post(
            "/api/resume/match",
            data={
                "job_text": "Software Developer",
                "job_skills": "Python,React",
                "job_title": "Software Developer",
                "job_category": "INFORMATION-TECHNOLOGY",
                "required_experience": "2",
                "candidate_category": "INFORMATION-TECHNOLOGY",
                "candidate_experience": "4",
                "candidate_title": "Software Engineer",
            },
            files={
                "file": (
                    "resume.txt",
                    b"Some resume text",
                    "text/plain",
                )
            },
        )

    assert response.status_code == 415


def test_resume_match_rejects_oversized_pdf():
    app = create_app(resource_factory=fake_resource_factory)

    with TestClient(app) as client:
        response = client.post(
            "/api/resume/match",
            data={
                "job_text": "Software Developer",
                "job_skills": "Python,React",
                "job_title": "Software Developer",
                "job_category": "INFORMATION-TECHNOLOGY",
                "required_experience": "2",
                "candidate_category": "INFORMATION-TECHNOLOGY",
                "candidate_experience": "4",
                "candidate_title": "Software Engineer",
            },
            files={
                "file": (
                    "large.pdf",
                    b"x" * (5 * 1024 * 1024 + 1),
                    "application/pdf",
                )
            },
        )

    assert response.status_code == 413