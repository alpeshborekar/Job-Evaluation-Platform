from __future__ import annotations
import re
import time
from dataclasses import dataclass

import google.generativeai as genai

from backend.config.settings import (
    GEMINI,
    SCORING_WEIGHTS,
    RECOMMENDATION_THRESHOLDS,
)

from backend.utils.errors import (
    ExternalServiceError,
    ProcessingError,
)

from backend.utils.logger import (
    get_logger,
)

logger = get_logger(__name__)

_STOP_WORDS = frozenset({
    "the", "and", "for", "with", "that", "this", "from", "are", "was",
    "were", "have", "has", "been", "will", "would", "could", "should",
    "also", "into", "more", "than", "its", "our", "your", "their",
})

_EXPERIENCE_SIGNALS = frozenset({
    "years",
    "experience",
    "worked",
    "developed",
    "led",
    "managed",
    "built",
    "designed",
    "implemented",
    "delivered",
    "achieved",
    "responsible",
    "maintained",
    "deployed",
    "architected",
})


@dataclass
class EvalResult:
    total_score: float
    skills_score: float
    experience_score: float
    keyword_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    recommendation: str
    reasoning: str
    ai_feedback: str
    processing_ms: int = 0


class EvaluationService:

    def evaluate(
        self,
        *,
        resume_text: str,
        job_description: str,
        resume_skills: list[str] | None = None,
    ) -> EvalResult:

        t0 = time.monotonic()

        if not resume_text or not job_description:
            raise ProcessingError(
                "resume_text and job_description are both required."
            )

        jd_skills = self._extract_skills(
            job_description
        )

        resume_skills = (
            resume_skills
            or self._extract_skills(
                resume_text
            )
        )

        logger.info(
            "JD Skills: %s",
            jd_skills,
        )

        logger.info(
            "Resume Skills: %s",
            resume_skills,
        )

        skills_score = self._score_skills(
            resume_skills,
            jd_skills,
        )

        experience_score = self._score_experience(
            resume_text,
            job_description,
        )

        keyword_score = self._score_keywords(
            resume_text,
            job_description,
        )

        w = SCORING_WEIGHTS

        total = (
            skills_score * w["skills_match"]
            + experience_score * w["experience_relevance"]
            + keyword_score * w["keyword_relevance"]
        )

        total = round(
            min(total, 100.0),
            2,
        )

        resume_set = {
            s.strip().lower()
            for s in resume_skills
            if s
        }

        jd_set = {
            s.strip().lower()
            for s in jd_skills
            if s
        }

        matched = sorted(
            list(resume_set & jd_set)
        )

        missing = sorted(
            list(jd_set - resume_set)
        )

        recommendation = self._recommend(
            total
        )

        reasoning = self._build_reasoning(
            total,
            skills_score,
            experience_score,
            keyword_score,
            matched,
            missing,
            recommendation,
        )

        ai_feedback = self._get_ai_feedback(
            resume_text,
            job_description,
            total,
        )

        elapsed_ms = int(
            (
                time.monotonic() - t0
            ) * 1000
        )

        logger.info(
            (
                "Evaluation complete "
                "score=%.1f rec=%s "
                "skills=%.1f exp=%.1f "
                "kw=%.1f ms=%d"
            ),
            total,
            recommendation,
            skills_score,
            experience_score,
            keyword_score,
            elapsed_ms,
        )

        return EvalResult(
            total_score=total,
            skills_score=round(
                skills_score,
                2,
            ),
            experience_score=round(
                experience_score,
                2,
            ),
            keyword_score=round(
                keyword_score,
                2,
            ),
            matched_skills=matched,
            missing_skills=missing,
            recommendation=recommendation,
            reasoning=reasoning,
            ai_feedback=ai_feedback,
            processing_ms=elapsed_ms,
        )

    def _extract_skills(
        self,
        text: str,
    ) -> list[str]:

        text_lower = text.lower()

        skills_db = [
            "python",
            "javascript",
            "typescript",
            "java",
            "go",
            "rust",
            "c++",
            "c#",
            "react",
            "reactjs",
            "nodejs",
            "flask",
            "django",
            "fastapi",
            "mongodb",
            "sql",
            "nosql",
            "git",
            "html",
            "css",
            "docker",
            "kubernetes",
            "aws",
            "azure",
            "gcp",
            "redis",
            "rest api",
            "graphql",
            "linux",
            "bash",
            "tensorflow",
            "pytorch",
        ]

        found = []

        for skill in skills_db:

            if skill.lower() in text_lower:
                found.append(
                    skill.lower()
                )

        return sorted(
            set(found)
        )

    def _score_skills(
        self,
        resume_skills: list[str],
        jd_skills: list[str],
    ) -> float:

        if not jd_skills:
            return 50.0

        resume_set = {
            s.strip().lower()
            for s in resume_skills
            if s
        }

        jd_set = {
            s.strip().lower()
            for s in jd_skills
            if s
        }

        matched = (
            resume_set & jd_set
        )

        logger.info(
            "Matched skills: %s",
            matched,
        )

        score = (
            len(matched)
            / len(jd_set)
        ) * 100

        return min(
            score,
            100.0,
        )

    def _score_experience(
        self,
        resume_text: str,
        job_description: str,
    ) -> float:

        resume_tokens = self._tokenize(
            resume_text
        )

        jd_tokens = self._tokenize(
            job_description
        )

        resume_signals = (
            resume_tokens
            & _EXPERIENCE_SIGNALS
        )

        jd_signals = (
            jd_tokens
            & _EXPERIENCE_SIGNALS
        )

        if not jd_signals:
            return 50.0

        overlap = len(
            resume_signals
            & jd_signals
        )

        score = min(
            overlap / len(jd_signals),
            1.0,
        ) * 100

        word_bonus = min(
            len(
                resume_text.split()
            ) / 500,
            1.0,
        ) * 10

        return min(
            score + word_bonus,
            100.0,
        )

    def _score_keywords(
        self,
        resume_text: str,
        job_description: str,
    ) -> float:

        jd_freq = self._term_frequency(
            job_description
        )

        resume_set = self._tokenize(
            resume_text
        )

        if not jd_freq:
            return 0.0

        total_weight = sum(
            jd_freq.values()
        )

        matched_weight = sum(
            freq
            for term, freq in jd_freq.items()
            if term in resume_set
        )

        return (
            matched_weight
            / total_weight
        ) * 100

    def _recommend(
        self,
        score: float,
    ) -> str:

        t = RECOMMENDATION_THRESHOLDS

        if score >= t["hire"]:
            return "Hire"

        if score >= t["improve"]:
            return "Improve"

        return "Reject"

    def _build_reasoning(
        self,
        total: float,
        skills: float,
        experience: float,
        keywords: float,
        matched: list[str],
        missing: list[str],
        rec: str,
    ) -> str:

        lines = [
            f"Overall match score: {total:.1f}/100.",
            (
                f"Skills alignment: "
                f"{skills:.1f}/100."
            ),
            (
                f"Experience relevance: "
                f"{experience:.1f}/100."
            ),
            (
                f"Keyword coverage: "
                f"{keywords:.1f}/100."
            ),
        ]

        if matched:
            lines.append(
                (
                    "Key matching skills: "
                    f"{', '.join(matched[:8])}."
                )
            )

        if missing:
            lines.append(
                (
                    "Critical gaps: "
                    f"{', '.join(missing[:8])}."
                )
            )

        lines.append(
            f"Recommendation: {rec}."
        )

        return " ".join(
            lines
        )

    def _get_ai_feedback(
        self,
        resume_text: str,
        job_description: str,
        score: float,
    ) -> str:

        if not GEMINI.api_key:
            return (
                "AI feedback unavailable "
                "(API key not configured)."
            )

        try:

            genai.configure(
                api_key=GEMINI.api_key
            )

            model = (
                genai.GenerativeModel(
                    GEMINI.model
                )
            )

            prompt = (
                f"You are a senior hiring manager. "
                f"A candidate scored {score:.1f}/100 "
                f"for the following job.\n\n"
                f"JOB DESCRIPTION:\n"
                f"{job_description[:800]}\n\n"
                f"RESUME:\n"
                f"{resume_text[:1200]}\n\n"
                f"Provide actionable feedback."
            )

            response = model.generate_content(
                prompt
            )

            return response.text.strip()

        except Exception as exc:

            logger.warning(
                "Gemini AI feedback failed: %s",
                exc,
            )

            # return (
            #     "AI feedback temporarily "
            #     f"unavailable: {exc}"
            # )
            return (
    "AI feedback service is "
    "currently unavailable."
)

    @staticmethod
    def _tokenize(
        text: str,
    ) -> set[str]:

        tokens = re.findall(
            r"\b[a-z]{3,}\b",
            text.lower(),
        )

        return {
            t
            for t in tokens
            if t not in _STOP_WORDS
        }

    @staticmethod
    def _term_frequency(
        text: str,
    ) -> dict[str, int]:

        from collections import Counter

        tokens = re.findall(
            r"\b[a-z]{3,}\b",
            text.lower(),
        )

        return dict(
            Counter(
                t
                for t in tokens
                if t not in _STOP_WORDS
            )
        )