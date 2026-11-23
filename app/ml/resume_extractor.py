
import re
import calendar
from datetime import date
from app.ml.skill_aliases import SKILL_ALIASES


# A deliberately controlled starter vocabulary.
# We can expand this using the ESCO taxonomy later.
SKILL_VOCABULARY = [
    # Programming languages
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#",
    "PHP", "Ruby", "Go",

    # Frontend
    "HTML", "HTML5", "CSS", "CSS3", "Tailwind CSS",
    "React", "Next.js", "Angular", "Vue.js",
    "Bootstrap", "Redux",

    # Backend and APIs
    "Node.js", "FastAPI", "Django", "Flask",
    "REST API", "API Development",
    "RESTful APIs", "GraphQL",

    # Databases and caching
    "SQL", "NoSQL", "PostgreSQL", "MySQL",
    "MongoDB", "Redis", "SQLite",

    # Cloud and infrastructure
    "AWS", "AWS S3", "SQS", "Azure",
    "Google Cloud", "Docker", "Kubernetes",
    "Linux", "CI/CD",

    # Mobile and emerging technologies
    "Flutter", "Capacitor", "ARCore",
    "Augmented Reality", "Generative AI",

    # AI and data science
    "Google Gemini", "Artificial Intelligence",
    "Machine Learning", "Deep Learning",
    "Natural Language Processing",
    "Data Science", "Data Analysis", "Data Analytics",
    "Pandas", "NumPy", "Scikit-learn",
    "TensorFlow", "PyTorch",

    # Developer tools
    "Git", "GitHub", "Swagger", "Postman",
    "Visual Studio Code",

    # Other skills
    "Communication", "Project Management",
    "Problem Solving", "Data Visualization",
    "Financial Analysis", "Business Development",
    "Sales", "Recruitment", "Employee Relations",
]

TITLE_KEYWORDS = [
    "engineer",
    "developer",
    "analyst",
    "manager",
    "designer",
    "consultant",
    "administrator",
    "specialist",
    "architect",
    "recruiter",
    "accountant",
    "scientist",
    "coordinator",
    "executive",
    "officer",
    "technician",
    "intern",
]


class ResumeExtractor:
    def __init__(self, skill_vocabulary=None):
        self.skill_vocabulary = skill_vocabulary or SKILL_VOCABULARY

    @staticmethod
    def _normalize_text(text):
        return re.sub(r"\s+", " ", text.casefold()).strip()

    @staticmethod
    def _make_phrase_pattern(phrase):
        escaped = re.escape(phrase.casefold())
        escaped = escaped.replace(r"\ ", r"\s+")

        return re.compile(
            rf"(?<![a-z0-9]){escaped}(?![a-z0-9])",
            re.IGNORECASE,
        )

    MONTHS = {
        month.casefold(): index
        for index, month in enumerate(calendar.month_name)
        if month
    }

    MONTHS.update({
        month.casefold(): index
        for index, month in enumerate(calendar.month_abbr)
        if month
    })

    def _parse_resume_date(self, month, year):
        """Convert a month/year pair into a date."""

        year = int(year)

        if month:
            month_number = self.MONTHS[month.casefold()]
        else:
            month_number = 1

        return date(year, month_number, 1)

    def _get_experience_section(self, text):
        """Extract professional experience section only."""

        lines = text.splitlines()

        start = None
        end = len(lines)

        section_endings = {
            "projects",
            "education",
            "achievements",
            "certifications",
            "technical skills",
        }

        for index, line in enumerate(lines):
            heading = line.strip().casefold()

            if heading in {
                "professional experience",
                "work experience",
                "employment history",
            }:
                start = index + 1
                continue

            if start is not None and heading in section_endings:
                end = index
                break

        if start is None:
            return ""

        return "\n".join(lines[start:end])

    def _calculate_months(self, start_date, end_date):
        """Calculate elapsed months between two dates."""

        return max(
            0,
            (end_date.year - start_date.year) * 12
            + end_date.month - start_date.month
        )
    
    def extract_skills(self, text):
        if not isinstance(text, str):
            raise ValueError("Resume text must be a string.")

        if not text.strip():
            raise ValueError("Resume text cannot be empty.")

        # Map normalized aliases to their canonical skill names.
        canonical_skills = {}

        for skill in self.skill_vocabulary:
            canonical_skills[skill.casefold()] = skill

        # Preserve the preferred display format for aliases.
        display_names = {
            skill.casefold(): skill
            for skill in self.skill_vocabulary
        }

        for alias, canonical in SKILL_ALIASES.items():
            display_name = display_names.get(
                canonical.casefold(),
                canonical,
            )

            canonical_skills[alias.casefold()] = display_name

        matches = []

        for searchable_skill, canonical_skill in canonical_skills.items():
            pattern = self._make_phrase_pattern(searchable_skill)

            match = pattern.search(text)

            if match:
                matches.append(
                    (match.start(), canonical_skill)
                )

        # Preserve the order in which skills first appear.
        matches.sort(key=lambda item: item[0])

        extracted_skills = []
        seen = set()

        for _, skill in matches:
            normalized = skill.casefold()

            if normalized not in seen:
                extracted_skills.append(skill)
                seen.add(normalized)

        return extracted_skills

    def extract_experience(self, text):
        if not isinstance(text, str):
            raise ValueError("Resume text must be a string.")

        if not text.strip():
            raise ValueError("Resume text cannot be empty.")

        explicit_patterns = [
            r"\b(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)"
            r"\s*(?:of\s+)?(?:professional\s+|work(?:ing)?\s+)?experience\b",

            r"\bexperience\s*[:\-]\s*(\d+(?:\.\d+)?)"
            r"\s*\+?\s*(?:years?|yrs?)\b",
        ]

        explicit_values = []

        for pattern in explicit_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)

            explicit_values.extend(
                float(value) for value in matches
            )

        # Extract employment dates only from the
        # professional experience section.
        experience_section = self._get_experience_section(text)

        month_pattern = (
            r"January|February|March|April|May|June|July|August|"
            r"September|October|November|December|"
            r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
        )

        date_range_pattern = re.compile(
            rf"\b(?:(?P<start_month>{month_pattern})\s+)?"
            rf"(?P<start_year>19\d{{2}}|20\d{{2}})"
            rf"\s*(?:-|–|—|to)\s*"
            rf"(?:(?P<end_month>{month_pattern})\s+)?"
            rf"(?P<end_year>19\d{{2}}|20\d{{2}})"
            rf"|"
            rf"\b(?:(?P<start_month2>{month_pattern})\s+)?"
            rf"(?P<start_year2>19\d{{2}}|20\d{{2}})"
            rf"\s*(?:-|–|—|to)\s*"
            rf"(?P<present>present|current|till date|to date)\b",
            re.IGNORECASE,
        )

        employment_periods = []
        date_evidence = []

        today = date.today()

        for match in date_range_pattern.finditer(experience_section):
            groups = match.groupdict()

            start_month = (
                groups["start_month"]
                or groups["start_month2"]
            )

            start_year = (
                groups["start_year"]
                or groups["start_year2"]
            )

            start_date = self._parse_resume_date(
                start_month,
                start_year,
            )

            if groups["present"]:
                end_date = date(today.year, today.month, 1)
            else:
                end_date = self._parse_resume_date(
                    groups["end_month"],
                    groups["end_year"],
                )

            if end_date < start_date:
                continue

            employment_periods.append((start_date, end_date))
            date_evidence.append(match.group(0).strip())

        # Merge overlapping employment periods so that
        # simultaneous jobs are not counted twice.
        employment_periods.sort(key=lambda period: period[0])

        merged_periods = []

        for start_date, end_date in employment_periods:
            if (
                merged_periods
                and start_date <= merged_periods[-1][1]
            ):
                previous_start, previous_end = merged_periods[-1]

                merged_periods[-1] = (
                    previous_start,
                    max(previous_end, end_date),
                )
            else:
                merged_periods.append((start_date, end_date))

        total_months = sum(
            self._calculate_months(start_date, end_date)
            for start_date, end_date in merged_periods
        )

        date_based_experience = total_months / 12

        # Use the larger estimate rather than adding explicit
        # experience claims to date-derived experience.
        experience_values = explicit_values.copy()

        if merged_periods:
            experience_values.append(date_based_experience)

        if not experience_values:
            return {
                "years_experience": None,
                "experience_evidence": [],
            }

        years_experience = max(experience_values)

        evidence = [
            f"{value:g} years"
            for value in explicit_values
        ]

        evidence.extend(date_evidence)

        return {
            "years_experience": round(years_experience, 2),
            "experience_evidence": evidence,
        }
    
    def extract_title(self, text):
        if not isinstance(text, str):
            raise ValueError("Resume text must be a string.")

        if not text.strip():
            raise ValueError("Resume text cannot be empty.")

        lines = text.splitlines()

        title_keywords = {
            "engineer", "developer", "analyst", "manager",
            "designer", "consultant", "administrator",
            "specialist", "architect", "recruiter",
            "accountant", "scientist", "coordinator",
            "executive", "officer", "technician", "intern",
        }

        for line in lines[:12]:
            line = line.strip()

            if not line or len(line) > 100:
                continue

            if "@" in line or re.search(r"\d{7,}", line):
                continue

            parts = re.split(r"\s*[|]\s*", line)

            title = parts[0].strip()

            words = set(re.findall(r"[a-z]+", title.casefold()))

            if words.intersection(title_keywords):
                specialization = (
                    parts[1].strip().title()
                    if len(parts) > 1 and parts[1].strip()
                    else None
                )

                return {
                    "candidate_title": title.title(),
                    "specialization": specialization,
                }

        return {
            "candidate_title": None,
            "specialization": None,
        }
    
    def analyze(self, text):
        if not isinstance(text, str):
            raise ValueError("Resume text must be a string.")

        if not text.strip():
            raise ValueError("Resume text cannot be empty.")

        skills = self.extract_skills(text)
        experience = self.extract_experience(text)
        title = self.extract_title(text)

        return {
            "skills": skills,
            "years_experience": experience["years_experience"],
            "experience_evidence": experience["experience_evidence"],
            "candidate_title": title["candidate_title"],
            "specialization": title["specialization"],
        }
