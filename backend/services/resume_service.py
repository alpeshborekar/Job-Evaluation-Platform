from __future__ import annotations

import os
import uuid
from dataclasses import dataclass

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from.config.settings import APP

from.repositories.resume_repo import (
    ResumeRepository,
)

from.utils.database import (
    db_session,
)

from.utils.errors import (
    AuthorizationError,
    ValidationError,
)

from.utils.file_parser import (
    parse_file,
)

from.utils.logger import (
    get_logger,
)

logger = get_logger(__name__)


@dataclass
class ParseResult:
    text: str
    word_count: int
    skills: list[str]


class ResumeService:

    def upload(
        self,
        file: FileStorage,
        *,
        user_id: int | None = None,
        email: str | None = None,
    ) -> dict:

        if not file:
            raise ValidationError(
                "No file uploaded."
            )

        filename = secure_filename(
            file.filename or ""
        )

        if not filename:
            raise ValidationError(
                "Invalid filename."
            )

        ext = (
            filename.rsplit(".", 1)[-1]
            .lower()
        )

        allowed = {
            "pdf",
            "docx",
        }

        if ext not in allowed:
            raise ValidationError(
                (
                    "Only PDF and DOCX "
                    "files are supported."
                )
            )

        os.makedirs(
            APP.upload_dir,
            exist_ok=True,
        )

        unique_name = (
            f"{uuid.uuid4().hex}.{ext}"
        )

        stored_path = os.path.join(
            APP.upload_dir,
            unique_name,
        )

        file.save(stored_path)

        result = self._parse_resume(
            stored_path
        )

        with db_session() as session:

            repo = ResumeRepository(
                session
            )

            resume = repo.create(
                user_id=user_id,
                original_name=filename,
                stored_path=stored_path,
                file_type=ext,
            )

            repo.mark_parsed(
                resume.id,
                parsed_text=result.text,
                skills_found=result.skills,
                word_count=result.word_count,
            )

            logger.info(
                (
                    "Resume uploaded "
                    "id=%s "
                    "skills=%s"
                ),
                resume.id,
                result.skills,
            )

            return {
                "id": resume.id,
                "filename": filename,
                "word_count": (
                    result.word_count
                ),
                "skills_found": (
                    result.skills
                ),
                "status": "completed",
            }

    def get(
        self,
        resume_id: int,
        *,
        requesting_user_id: int | None = None,
    ) -> dict:

        with db_session() as session:

            repo = ResumeRepository(
                session
            )

            resume = repo.get_by_id(
                resume_id
            )

            if (
                requesting_user_id
                and resume.user_id
                and resume.user_id
                != requesting_user_id
            ):
                raise AuthorizationError(
                    (
                        "Unauthorized "
                        "access."
                    )
                )

            return self._serialize(
                resume
            )

    def list_for_user(
        self,
        user_id: int,
        *,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:

        with db_session() as session:

            repo = ResumeRepository(
                session
            )

            resumes = repo.list_by_user(
                user_id,
                page=page,
                per_page=per_page,
            )

            total = repo.count_by_user(
                user_id
            )

            return {
                "items": [
                    self._serialize(r)
                    for r in resumes
                ],
                "total": total,
                "page": page,
                "per_page": per_page,
            }

    def _parse_resume(
        self,
        path: str,
    ) -> ParseResult:

        ext = (
            path.rsplit(".", 1)[-1]
            .lower()
        )

        parsed = parse_file(
            path,
            ext,
        )

        text = parsed.text

        if not text.strip():
            raise ValidationError(
                (
                    "Could not extract "
                    "text from resume."
                )
            )

        skills = (
            self._extract_skills_simple(
                text
            )
        )

        logger.info(
            (
                "Extracted resume "
                "skills: %s"
            ),
            skills,
        )

        word_count = len(
            text.split()
        )

        return ParseResult(
            text=text,
            word_count=word_count,
            skills=skills,
        )

    @staticmethod
    def _extract_skills_simple(
        text: str,
    ) -> list[str]:

        import re

        text = text.lower()

        skills_db = [
            "python",
            "javascript",
            "typescript",
            "java",
            "go",
            "rust",
            "react",
            "angular",
            "vue",
            "flask",
            "django",
            "fastapi",
            "mongodb",
            "postgresql",
            "sql",
            "nosql",
            "redis",
            "docker",
            "kubernetes",
            "aws",
            "azure",
            "gcp",
            "terraform",
            "git",
            "linux",
            "html",
            "css",
            "graphql",
            "rest api",
            "ci/cd",
            "devops",
            "machine learning",
            "deep learning",
            "nlp",
            "data science",
            "tensorflow",
            "pytorch",
            "pandas",
            "numpy",
            "spark",
            "celery",
            "rabbitmq",
            "elasticsearch",
        ]

        found = []

        for skill in skills_db:

            pattern = (
                r"\b"
                + re.escape(skill)
                + r"\b"
            )

            if re.search(
                pattern,
                text,
                re.IGNORECASE,
            ):

                found.append(skill)

        return sorted(
            list(set(found))
        )

    @staticmethod
    def _serialize(
        resume,
    ) -> dict:

        return {
            "id": resume.id,
            "original_name": (
                resume.original_name
            ),
            "file_type": (
                resume.file_type
            ),
            "parse_status": (
                resume.parse_status.value
                if resume.parse_status
                else None
            ),
            "skills_found": (
                resume.skills_found
                or []
            ),
            "word_count": (
                resume.word_count
            ),
            "uploaded_at": (
                resume.uploaded_at.isoformat()
                if resume.uploaded_at
                else None
            ),
        }