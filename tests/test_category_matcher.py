
import pytest

from app.ml.category_matcher import CategoryMatcher


@pytest.fixture
def matcher():
    return CategoryMatcher()


# CATEGORY MATCHING TESTS

def test_same_category(matcher):
    result = matcher.calculate_category_match(
        "INFORMATION-TECHNOLOGY",
        "information technology"
    )

    assert result["category_match"] is True
    assert result["category_score"] == 100.0


def test_different_categories(matcher):
    result = matcher.calculate_category_match(
        "FINANCE",
        "HR"
    )

    assert result["category_match"] is False
    assert result["category_score"] == 0.0


def test_category_case_and_whitespace(matcher):
    result = matcher.calculate_category_match(
        "  Finance  ",
        "FINANCE"
    )

    assert result["category_match"] is True


def test_empty_category(matcher):
    with pytest.raises(ValueError):
        matcher.calculate_category_match("", "FINANCE")


# TITLE MATCHING TESTS

def test_identical_titles(matcher):
    result = matcher.calculate_title_similarity(
        "Data Scientist",
        "Data Scientist"
    )

    assert result["title_similarity"] == 1.0
    assert result["title_score"] == 100.0


def test_similar_titles(matcher):
    result = matcher.calculate_title_similarity(
        "Data Scientist",
        "Senior Data Scientist"
    )

    assert result["title_similarity"] > 0
    assert result["title_score"] > 0


def test_unrelated_titles(matcher):
    result = matcher.calculate_title_similarity(
        "Data Scientist",
        "HR Manager"
    )

    assert result["title_similarity"] < 0.5


def test_empty_title(matcher):
    with pytest.raises(ValueError):
        matcher.calculate_title_similarity(
            "",
            "Data Scientist"
        )

def test_normalize_senior_abbreviation():
    matcher = CategoryMatcher()
    assert matcher.normalize_text("Sr.Officer") == "senior officer"


def test_normalize_assistant_abbreviation():
    matcher = CategoryMatcher()
    assert matcher.normalize_text("Asst. Manager") == "assistant manager"


def test_remove_parenthesized_abbreviation():
    matcher = CategoryMatcher()
    assert matcher.normalize_text(
        "Database Administrator (DBA)"
    ) == "database administrator"


def test_preserve_technology_specialization():
    matcher = CategoryMatcher()
    assert matcher.normalize_text(
        "Full Stack Developer (Python,React js)"
    ) == "full stack developer python react js"
