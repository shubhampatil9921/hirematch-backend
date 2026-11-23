
from dataclasses import dataclass
from pathlib import Path

from sentence_transformers import SentenceTransformer

from app.ml.category_matcher import CategoryMatcher
from app.ml.esco_vocabulary import ESCOVocabulary
from app.ml.experience_matcher import ExperienceMatcher
from app.ml.semantic_skill_matcher import SemanticSkillMatcher
from app.ml.semantic_title_matcher import SemanticTitleMatcher
from app.ml.tfidf_matcher import TfidfMatcher
from app.services.matching_service import MatchingService


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ESCO_PATH = (
    PROJECT_ROOT / "data" / "raw" / "esco" / "skills_en.csv"
)


@dataclass
class AppResources:
    embedding_model: object
    esco_vocabulary: object
    matching_service: MatchingService


def create_resources(
    model=None,
    esco_vocabulary=None,
    esco_path=ESCO_PATH,
):
    """
    Initialize shared ML resources and the matching service.

    Optional dependencies allow lightweight testing without
    downloading or loading the actual ML model.
    """

    # 1. Load the semantic model only if one was not injected.
    if model is None:
        model = SentenceTransformer(MODEL_NAME)

    # 2. Load ESCO vocabulary only if one was not injected.
    if esco_vocabulary is None:
        if not Path(esco_path).is_file():
            raise FileNotFoundError(
                f"ESCO vocabulary file not found: {esco_path}"
            )

        esco_vocabulary = ESCOVocabulary(esco_path)

    # 3. Build semantic matchers using the SAME model instance.
    skill_matcher = SemanticSkillMatcher(
        model=model,
        esco_vocabulary=esco_vocabulary,
    )

    title_matcher = SemanticTitleMatcher(
        model=model,
    )

    # 4. Initialize the remaining matching components.
    matching_service = MatchingService(
        tfidf_matcher=TfidfMatcher(),
        skill_matcher=skill_matcher,
        experience_matcher=ExperienceMatcher(),
        category_matcher=CategoryMatcher(),
        title_matcher=title_matcher,
    )

    return AppResources(
        embedding_model=model,
        esco_vocabulary=esco_vocabulary,
        matching_service=matching_service,
    )
