from pydantic import BaseModel, ConfigDict, Field, field_validator


class MatchingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resume_text: str = Field(min_length=1, max_length=50000)
    job_text: str = Field(min_length=1, max_length=50000)

    resume_skills: list[str] = Field(default_factory=list, max_length=200)
    job_skills: list[str] = Field(default_factory=list, max_length=200)

    candidate_experience: float = Field(ge=0, allow_inf_nan=False)
    required_experience: float = Field(ge=0, allow_inf_nan=False)

    candidate_category: str = Field(min_length=1, max_length=200)
    job_category: str = Field(min_length=1, max_length=200)

    candidate_title: str = Field(min_length=1, max_length=200)
    job_title: str = Field(min_length=1, max_length=200)

    @field_validator(
        "resume_text",
        "job_text",
        "candidate_category",
        "job_category",
        "candidate_title",
        "job_title",
    )
    @classmethod
    def validate_non_blank_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field cannot contain only whitespace.")

        return value

    @field_validator("resume_skills", "job_skills")
    @classmethod
    def validate_skills(cls, skills: list[str]) -> list[str]:
        cleaned_skills = []

        for skill in skills:
            skill = skill.strip()

            if not skill:
                raise ValueError("Skill entries cannot be empty.")

            cleaned_skills.append(skill)

        return cleaned_skills


class ScoreComponent(BaseModel):
    score: float = Field(ge=0, le=100, allow_inf_nan=False)
    weight: float = Field(ge=0, le=100, allow_inf_nan=False)
    weighted_score: float = Field(ge=0, le=100, allow_inf_nan=False)


class SemanticSkillMatch(BaseModel):
    resume_skill: str
    job_skill: str
    similarity: float = Field(ge=0, le=1, allow_inf_nan=False)


class SkillMatchResult(BaseModel):
    exact_matched_skills: list[str]
    semantic_matched_skills: list[SemanticSkillMatch]
    matched_skills: list[str]
    missing_skills: list[str]
    total_required_skills: int = Field(ge=0)
    exact_match_count: int = Field(ge=0)
    semantic_match_count: int = Field(ge=0)
    matched_count: int = Field(ge=0)
    missing_count: int = Field(ge=0)
    skill_coverage: float = Field(ge=0, le=100, allow_inf_nan=False)


class ExperienceMatchResult(BaseModel):
    candidate_experience: float = Field(ge=0, allow_inf_nan=False)
    required_experience: float = Field(ge=0, allow_inf_nan=False)
    meets_requirement: bool
    experience_gap: float = Field(ge=0, allow_inf_nan=False)
    experience_score: float = Field(ge=0, le=100, allow_inf_nan=False)


class CategoryMatchResult(BaseModel):
    candidate_category: str
    job_category: str
    category_match: bool
    category_score: float = Field(ge=0, le=100, allow_inf_nan=False)


class TitleMatchResult(BaseModel):
    candidate_title: str
    job_title: str
    title_similarity: float = Field(ge=0, le=1, allow_inf_nan=False)
    title_score: float = Field(ge=0, le=100, allow_inf_nan=False)


class MatchingResponse(BaseModel):
    overall_score: float = Field(ge=0, le=100, allow_inf_nan=False)
    score_breakdown: dict[str, ScoreComponent]
    text_similarity: float = Field(ge=0, le=1, allow_inf_nan=False)
    skill_match: SkillMatchResult
    experience_match: ExperienceMatchResult
    category_match: CategoryMatchResult
    title_match: TitleMatchResult
    score_interpretation: str


class ResumeAnalysisResponse(BaseModel):
    filename: str
    extracted_text: str
    page_count: int
    character_count: int
    skills: list[str]
    years_experience: float | None
    experience_evidence: list[str]
    candidate_title: str | None
    specialization: str | None = None