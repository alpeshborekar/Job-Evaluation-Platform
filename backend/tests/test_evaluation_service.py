import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import patch

from services.evaluation_service import EvaluationService

svc = EvaluationService()

STRONG_RESUME = """
Senior Python Engineer with 6 years of experience.
Developed and deployed Flask, FastAPI microservices on AWS using Docker and Kubernetes.
Led machine learning pipeline using TensorFlow and PyTorch on large-scale datasets.
Proficient in PostgreSQL, Redis, Kafka, and Elasticsearch.
Implemented CI/CD pipelines with GitHub Actions and Terraform.
"""

WEAK_RESUME = """
I enjoy art and cooking. I have done some Excel spreadsheets at my part-time job.
Good communicator. Looking for opportunities.
"""

JOB_DESCRIPTION = """
We are looking for a Senior Backend Engineer with strong Python experience.
The ideal candidate has worked with Flask or FastAPI, deployed services on AWS,
and is comfortable with Docker and Kubernetes. Experience with PostgreSQL, Redis,
and machine learning pipelines (TensorFlow, PyTorch) is a strong plus.
CI/CD knowledge (Terraform, GitHub Actions) required. 5+ years of experience expected.
"""


class TestSkillExtraction:
    def test_extracts_python(self):
        skills = svc._extract_skills("Experienced Python developer")
        assert "python" in skills

    def test_extracts_multiword(self):
        skills = svc._extract_skills("Expert in machine learning and deep learning")
        assert "machine learning" in skills

    def test_empty_text(self):
        assert svc._extract_skills("") == []


class TestScoringComponents:
    def test_perfect_skills_overlap(self):
        skills = ["python", "flask", "docker"]

        score = svc._score_skills(skills, skills)

        assert score == 100.0

    def test_zero_skills_overlap(self):
        score = svc._score_skills(["excel"], ["python", "flask"])

        assert score == 0.0

    def test_partial_overlap(self):
        score = svc._score_skills(["python", "excel"], ["python", "flask"])

        assert 0 < score < 100

    def test_no_jd_skills_returns_neutral(self):
        score = svc._score_skills(["python"], [])

        assert score == 50.0


class TestRecommendation:
    def test_hire(self):
        assert svc._recommend(80) == "Hire"

    def test_improve(self):
        assert svc._recommend(55) == "Improve"

    def test_reject(self):
        assert svc._recommend(30) == "Reject"

    def test_boundary_hire(self):
        assert svc._recommend(75) == "Hire"

    def test_boundary_improve(self):
        assert svc._recommend(45) == "Improve"

    def test_boundary_reject(self):
        assert svc._recommend(44) == "Reject"


class TestEndToEnd:
    # Mock AI response to avoid external API calls
    @patch.object(EvaluationService, "_get_ai_feedback", return_value="mock feedback")
    def test_strong_resume_scores_higher(self, _mock):
        strong = svc.evaluate(
            resume_text=STRONG_RESUME,
            job_description=JOB_DESCRIPTION,
        )

        weak = svc.evaluate(
            resume_text=WEAK_RESUME,
            job_description=JOB_DESCRIPTION,
        )

        assert strong.total_score > weak.total_score

    @patch.object(EvaluationService, "_get_ai_feedback", return_value="mock feedback")
    def test_strong_resume_recommendation(self, _mock):
        result = svc.evaluate(
            resume_text=STRONG_RESUME,
            job_description=JOB_DESCRIPTION,
        )

        assert result.recommendation in ("Hire", "Improve")

    @patch.object(EvaluationService, "_get_ai_feedback", return_value="mock feedback")
    def test_weak_resume_recommendation(self, _mock):
        result = svc.evaluate(
            resume_text=WEAK_RESUME,
            job_description=JOB_DESCRIPTION,
        )

        assert result.recommendation == "Reject"

    @patch.object(EvaluationService, "_get_ai_feedback", return_value="mock feedback")
    def test_result_structure(self, _mock):
        result = svc.evaluate(
            resume_text=STRONG_RESUME,
            job_description=JOB_DESCRIPTION,
        )

        assert 0 <= result.total_score <= 100
        assert isinstance(result.matched_skills, list)
        assert isinstance(result.missing_skills, list)
        assert result.reasoning

    def test_raises_on_empty_input(self):
        with pytest.raises(Exception):
            svc.evaluate(resume_text="", job_description="")