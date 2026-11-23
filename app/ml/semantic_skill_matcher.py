
import re

import numpy as np
from sentence_transformers import SentenceTransformer

from app.ml.skill_aliases import SKILL_ALIASES


class SemanticSkillMatcher:
    """
    Match resume skills to job requirements using:
    1. Exact matching
    2. Verified skill aliases
    3. Semantic similarity for remaining skills
    """

    def __init__(
        self,
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        threshold=0.82,
        model=None,
        esco_vocabulary=None
    ):
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1.")

        self.threshold = threshold
        self.model = (
            model if model is not None
            else SentenceTransformer(model_name)
        )
        self.embedding_cache = {}
        self.esco_vocabulary = esco_vocabulary

    @staticmethod
    def normalize_skill(skill):
        if not isinstance(skill, str):
            return ""

        skill = skill.casefold().strip()
        skill = re.sub(r"\s+", " ", skill)

        return skill

    def canonicalize_skill(self, skill):
        """
        Resolve skills using manual aliases first,
        then unambiguous ESCO concepts.
        """

        normalized = self.normalize_skill(skill)

        if not normalized:
            return ""

        # 1. Manually verified aliases take priority.
        if normalized in SKILL_ALIASES:
            return SKILL_ALIASES[normalized]

        # 2. Resolve through ESCO if available.
        if self.esco_vocabulary is not None:
            concept = self.esco_vocabulary.resolve(normalized)

            if concept is not None:
                return self.normalize_skill(
                    concept["preferred_label"]
                )

        # 3. Fall back to normalized text.
        return normalized

    def _prepare_skills(self, skills):
        """
        Normalize, canonicalize and deduplicate skills.

        Returns a dictionary:
        canonical skill -> original display name
        """

        prepared = {}

        for skill in skills:
            normalized = self.normalize_skill(skill)

            if not normalized:
                continue

            canonical = self.canonicalize_skill(normalized)

            if canonical not in prepared:
                prepared[canonical] = skill.strip()

        return prepared

    def _get_embeddings(self, skills):
        """Encode only new skills and reuse cached embeddings."""

        missing_skills = [
            skill for skill in skills
            if skill not in self.embedding_cache
        ]

        if missing_skills:
            embeddings = self.model.encode(
                missing_skills,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False
            )

            for skill, embedding in zip(missing_skills, embeddings):
                self.embedding_cache[skill] = embedding

        return np.vstack([
            self.embedding_cache[skill]
            for skill in skills
        ])

    def calculate_skill_match(self, resume_skills, job_skills):

        if not isinstance(resume_skills, list):
            raise ValueError("Resume skills must be a list.")

        if not isinstance(job_skills, list):
            raise ValueError("Job skills must be a list.")

        # Canonical skill names mapped to original display names.
        candidate_map = self._prepare_skills(resume_skills)
        requirement_map = self._prepare_skills(job_skills)

        candidate_skills = list(candidate_map.keys())
        required_skills = list(requirement_map.keys())

        candidate_set = set(candidate_skills)

        # 1. Exact and verified-alias matches.
        exact_matches = [
            skill for skill in required_skills
            if skill in candidate_set
        ]

        unmatched_candidates = [
            skill for skill in candidate_skills
            if skill not in exact_matches
        ]

        unmatched_requirements = [
            skill for skill in required_skills
            if skill not in exact_matches
        ]

        # 2. Semantic matching for remaining skills.
        semantic_matches = []

        if unmatched_candidates and unmatched_requirements:

            candidate_embeddings = self._get_embeddings(
                unmatched_candidates
            )

            job_embeddings = self._get_embeddings(
                unmatched_requirements
            )

            similarity_matrix = (
                candidate_embeddings @ job_embeddings.T
            )

            candidate_indices, job_indices = np.unravel_index(
                np.argsort(similarity_matrix, axis=None)[::-1],
                similarity_matrix.shape
            )

            used_candidates = set()
            used_requirements = set()

            for candidate_idx, job_idx in zip(
                candidate_indices, job_indices
            ):

                score = float(
                    similarity_matrix[candidate_idx, job_idx]
                )

                if score < self.threshold:
                    break

                if (
                    candidate_idx in used_candidates
                    or job_idx in used_requirements
                ):
                    continue

                candidate_canonical = unmatched_candidates[candidate_idx]
                job_canonical = unmatched_requirements[job_idx]

                semantic_matches.append({
                    "resume_skill": candidate_map[candidate_canonical],
                    "job_skill": requirement_map[job_canonical],
                    "similarity": round(score, 4)
                })

                used_candidates.add(candidate_idx)
                used_requirements.add(job_idx)

        # 3. Build results using original display names.
        exact_matched_skills = [
            requirement_map[skill]
            for skill in exact_matches
        ]

        semantic_matched_skills = [
            match["job_skill"]
            for match in semantic_matches
        ]

        matched_skills = (
            exact_matched_skills + semantic_matched_skills
        )

        matched_canonical = set(exact_matches)

        matched_canonical.update(
            self.canonicalize_skill(match["job_skill"])
            for match in semantic_matches
        )

        missing_skills = [
            requirement_map[skill]
            for skill in required_skills
            if skill not in matched_canonical
        ]

        total_required = len(required_skills)
        matched_count = len(matched_skills)

        coverage = (
            matched_count / total_required * 100
            if total_required
            else 0.0
        )

        return {
            "exact_matched_skills": exact_matched_skills,
            "semantic_matched_skills": semantic_matches,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "total_required_skills": total_required,
            "exact_match_count": len(exact_matches),
            "semantic_match_count": len(semantic_matches),
            "matched_count": matched_count,
            "missing_count": len(missing_skills),
            "skill_coverage": round(coverage, 2)
        }
