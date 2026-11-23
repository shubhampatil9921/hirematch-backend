
import re


class SkillMatcher:

    def normalize_skill(self, skill):
        """Normalize skill names for consistent comparison."""

        if not isinstance(skill, str):
            return ""

        skill = skill.lower().strip()
        skill = re.sub(r"\s+", " ", skill)

        return skill

    def calculate_skill_match(self, resume_skills, job_skills):
        """
        Compare candidate skills with job-required skills.
        Return matched skills, missing skills and coverage.
        """

        if not isinstance(resume_skills, list):
            raise ValueError("Resume skills must be a list.")

        if not isinstance(job_skills, list):
            raise ValueError("Job skills must be a list.")

        candidate_skills = {
            self.normalize_skill(skill)
            for skill in resume_skills
            if self.normalize_skill(skill)
        }

        required_skills = list(dict.fromkeys(
            self.normalize_skill(skill)
            for skill in job_skills
            if self.normalize_skill(skill)
        ))

        matched_skills = [
            skill for skill in required_skills
            if skill in candidate_skills
        ]

        missing_skills = [
            skill for skill in required_skills
            if skill not in candidate_skills
        ]

        total_required = len(required_skills)

        if total_required == 0:
            coverage = 0.0
        else:
            coverage = (
                len(matched_skills) / total_required
            ) * 100

        return {
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "total_required_skills": total_required,
            "matched_count": len(matched_skills),
            "missing_count": len(missing_skills),
            "skill_coverage": round(coverage, 2)
        }
