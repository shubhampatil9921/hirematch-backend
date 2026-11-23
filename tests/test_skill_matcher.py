from app.ml.skill_matcher import SkillMatcher

matcher = SkillMatcher()


def test_normal_match():
    result = matcher.calculate_skill_match(
        ["Python", "SQL", "Java"],
        ["Python", "SQL", "Machine Learning", "Communication"]
    )
    assert result["skill_coverage"] == 50.0
    assert result["matched_count"] == 2


def test_case_and_whitespace():
    result = matcher.calculate_skill_match(
        ["  PYTHON ", " sql  "],
        ["python", "SQL"]
    )
    assert result["skill_coverage"] == 100.0


def test_duplicate_job_skills():
    result = matcher.calculate_skill_match(
        ["Python"],
        ["Python", "python", "Python"]
    )
    assert result["total_required_skills"] == 1
    assert result["skill_coverage"] == 100.0


def test_no_matching_skills():
    result = matcher.calculate_skill_match(
        ["Java"],
        ["Python", "SQL"]
    )
    assert result["matched_count"] == 0
    assert result["skill_coverage"] == 0.0


def test_empty_resume_skills():
    result = matcher.calculate_skill_match(
        [],
        ["Python", "SQL"]
    )
    assert result["skill_coverage"] == 0.0


def test_empty_job_skills():
    result = matcher.calculate_skill_match(
        ["Python", "SQL"],
        []
    )
    assert result["total_required_skills"] == 0
    assert result["skill_coverage"] == 0.0


def test_invalid_input():
    try:
        matcher.calculate_skill_match("Python", ["Python"])
        assert False, "Expected ValueError"
    except ValueError:
        pass


if __name__ == "__main__":
    test_normal_match()
    test_case_and_whitespace()
    test_duplicate_job_skills()
    test_no_matching_skills()
    test_empty_resume_skills()
    test_empty_job_skills()
    test_invalid_input()

    print("All 7 skill matcher tests passed!")