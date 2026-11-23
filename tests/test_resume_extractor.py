
import pytest

from app.ml.resume_extractor import ResumeExtractor
from datetime import date

@pytest.fixture
def extractor():
    return ResumeExtractor()


def test_extracts_technical_skills(extractor):
    text = """
    Software Engineer
    Experienced in Python, SQL, React, Docker and Machine Learning.
    """

    skills = extractor.extract_skills(text)

    assert "Python" in skills
    assert "SQL" in skills
    assert "React" in skills
    assert "Docker" in skills
    assert "Machine Learning" in skills


def test_extracts_skill_aliases(extractor):
    text = "Experienced in ML, NLP, JS and AI."

    skills = extractor.extract_skills(text)

    assert "Machine Learning" in skills
    assert "Natural Language Processing" in skills
    assert "JavaScript" in skills
    assert "Artificial Intelligence" in skills


def test_does_not_match_partial_words(extractor):
    text = "I enjoy scripting and working with databases."

    skills = extractor.extract_skills(text)

    assert "Python" not in skills
    assert "Java" not in skills
    assert "SQL" not in skills


def test_removes_duplicate_skills(extractor):
    text = "Python developer. Python, python and SQL."

    skills = extractor.extract_skills(text)

    assert skills.count("Python") == 1


def test_extracts_years_of_experience(extractor):
    text = "Software Engineer with 4 years of experience."

    result = extractor.extract_experience(text)

    assert result["years_experience"] == 4.0
    assert result["experience_evidence"] == ["4 years"]


def test_extracts_plus_years_experience(extractor):
    text = "5+ years of professional experience."

    result = extractor.extract_experience(text)

    assert result["years_experience"] == 5.0


def test_extracts_experience_label_format(extractor):
    text = "Experience: 3 years"

    result = extractor.extract_experience(text)

    assert result["years_experience"] == 3.0


def test_returns_none_when_experience_not_found(extractor):
    result = extractor.extract_experience(
        "Python developer with SQL knowledge."
    )

    assert result["years_experience"] is None
    assert result["experience_evidence"] == []


def test_extracts_candidate_title():
    extractor = ResumeExtractor()

    result = extractor.extract_title(
        "SHUBHAM PATIL\n"
        "SOFTWARE ENGINEER | FULL-STACK DEVELOPMENT\n"
        "Pune, India"
    )

    assert result == {
        "candidate_title": "Software Engineer",
        "specialization": "Full-Stack Development",
    }


def test_returns_none_when_title_not_found():
    extractor = ResumeExtractor()

    result = extractor.extract_title(
        "SHUBHAM PATIL\n"
        "Pune, India\n"
        "shubham@example.com"
    )

    assert result == {
        "candidate_title": None,
        "specialization": None,
    }

@pytest.mark.parametrize("invalid_text", ["", "   ", None, 123])
def test_rejects_invalid_resume_text(extractor, invalid_text):
    with pytest.raises(ValueError):
        extractor.analyze(invalid_text)


def test_extracts_experience_from_month_date_range():
    extractor = ResumeExtractor()

    result = extractor.extract_experience(
        """
        PROFESSIONAL EXPERIENCE
        Software Developer
        January 2025 – Present

        PROJECTS
        Student Project
        2021 – 2025
        """
    )

    expected_months = (
        (date.today().year - 2025) * 12
        + date.today().month - 1
    )

    assert result["years_experience"] == round(
        expected_months / 12,
        2,
    )

    assert "January 2025 – Present" in result["experience_evidence"]


def test_extracts_year_only_employment_range():
    extractor = ResumeExtractor()

    result = extractor.extract_experience(
        """
        PROFESSIONAL EXPERIENCE
        Developer
        2021 – 2023
        """
    )

    assert result["years_experience"] == 2.0


def test_does_not_count_education_dates():
    extractor = ResumeExtractor()

    result = extractor.extract_experience(
        """
        EDUCATION
        Bachelor of Engineering
        2021 – 2025
        """
    )

    assert result["years_experience"] is None


def test_does_not_double_count_overlapping_jobs():
    extractor = ResumeExtractor()

    result = extractor.extract_experience(
        """
        PROFESSIONAL EXPERIENCE
        Developer
        January 2022 – December 2023

        Consultant
        January 2023 – December 2024
        """
    )

    assert result["years_experience"] == 2.92