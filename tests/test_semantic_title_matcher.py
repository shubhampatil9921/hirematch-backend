
import pytest

from app.ml.semantic_title_matcher import SemanticTitleMatcher


@pytest.fixture
def matcher():
    # Test normalization without loading the ML model.
    return object.__new__(SemanticTitleMatcher)


def test_sde_expansion(matcher):
    assert matcher.normalize_title("SDE") == (
        "software development engineer"
    )


def test_swe_expansion(matcher):
    assert matcher.normalize_title("SWE") == "software engineer"


def test_dba_expansion(matcher):
    assert matcher.normalize_title("DBA") == (
        "database administrator"
    )


def test_ml_expansion(matcher):
    assert matcher.normalize_title("ML Engineer") == (
        "machine learning engineer"
    )


def test_ai_expansion(matcher):
    assert matcher.normalize_title("AI Engineer") == (
        "artificial intelligence engineer"
    )


def test_seniority_abbreviation(matcher):
    assert matcher.normalize_title("Sr. Software Engineer") == (
        "senior software engineer"
    )


def test_case_and_whitespace(matcher):
    assert matcher.normalize_title("  SDE  ") == (
        "software development engineer"
    )


def test_word_boundary_preserved(matcher):
    assert matcher.normalize_title("device engineer") == (
        "device engineer"
    )


@pytest.mark.parametrize("title", ["", "   ", None, 123])
def test_invalid_title(matcher, title):
    with pytest.raises(ValueError, match="Title cannot be empty"):
        matcher.normalize_title(title)
