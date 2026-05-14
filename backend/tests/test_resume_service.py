import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from services.resume_service import ResumeService
from unittest.mock import MagicMock

svc = ResumeService()


class TestSkillExtraction:
    def test_finds_python(self):
        result = svc._extract_skills_simple(
            "Experienced Python developer"
        )

        assert "Python" in result

    def test_finds_multiple(self):
        text = "Built Flask APIs deployed on AWS with Docker"

        result = svc._extract_skills_simple(text)

        assert "Flask" in result
        assert "AWS" in result
        assert "Docker" in result

    def test_case_insensitive(self):
        result = svc._extract_skills_simple(
            "used python and flask for backend"
        )

        assert "Python" in result
        assert "Flask" in result

    def test_empty_text_returns_empty(self):
        assert svc._extract_skills_simple("") == []

    def test_no_false_positives(self):
        result = svc._extract_skills_simple(
            "I enjoy hiking and cooking"
        )

        assert result == []

    def test_returns_list(self):
        result = svc._extract_skills_simple(
            "Python React SQL"
        )

        assert isinstance(result, list)

    def test_no_duplicates(self):
        result = svc._extract_skills_simple(
            "Python Python Python Flask Flask"
        )

        assert result.count("Python") == 1
        assert result.count("Flask") == 1


class TestTextCleaning:
    # Test helper used in file parsing
    def test_collapse_spaces(self):
        from utils.file_parser import _clean_text

        assert _clean_text(
            "hello   world"
        ) == "hello world"

    def test_collapse_newlines(self):
        from utils.file_parser import _clean_text

        result = _clean_text(
            "line1\n\n\n\n\nline2"
        )

        assert result == "line1\n\nline2"

    def test_strip_edges(self):
        from utils.file_parser import _clean_text

        assert _clean_text(
            "   hello   "
        ) == "hello"


class TestFileValidation:
    from unittest.mock import MagicMock

    # Create mock upload file
    def _mock_file(
        self,
        filename: str,
        size_bytes: int = 100,
    ):
        from unittest.mock import MagicMock

        f = MagicMock()

        f.filename = filename
        f.seek = MagicMock()
        f.tell = MagicMock(return_value=size_bytes)
        f.save = MagicMock()

        return f

    def test_rejects_txt_file(self):
        from utils.file_parser import save_upload
        from utils.errors import UnsupportedFileTypeError

        with pytest.raises(UnsupportedFileTypeError):
            save_upload(
                self._mock_file("resume.txt")
            )

    def test_rejects_oversized_file(self):
        from utils.file_parser import save_upload
        from utils.errors import FileTooLargeError

        # 15 MB exceeds default limit
        big_file = self._mock_file(
            "resume.pdf",
            size_bytes=15 * 1024 * 1024,
        )

        with pytest.raises(FileTooLargeError):
            save_upload(big_file)

    def test_accepts_pdf(self):
        from utils.file_parser import save_upload
        import tempfile

        # Create temp upload directory
        with tempfile.TemporaryDirectory() as tmpdir:
            f = self._mock_file(
                "resume.pdf",
                size_bytes=1024,
            )

            # Prevent actual disk write
            f.save = MagicMock()

            os.environ["UPLOAD_DIR"] = tmpdir

            path, ext = save_upload(f)

            assert ext == "pdf"