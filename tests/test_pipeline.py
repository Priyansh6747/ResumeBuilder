import json
import os
import tempfile

from reportlab.pdfgen.canvas import Canvas

from resumebuilder.pipeline import build_resume
from tests.conftest import make_full_content, make_minimal_content


class TestPipeline:
    def test_end_to_end_creates_pdf(self):
        content = make_full_content()
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "content.json")
            pdf_path = os.path.join(tmpdir, "resume_draft.pdf")
            with open(json_path, "w") as f:
                json.dump(content, f)

            build_resume(json_path, pdf_path)

            assert os.path.isfile(pdf_path)
            assert os.path.getsize(pdf_path) > 0

    def test_single_page(self):
        content = make_minimal_content(experience_bullets=2, project_bullets=2,
                                       achievements=1, num_exp=1, num_proj=1)
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "content.json")
            pdf_path = os.path.join(tmpdir, "output.pdf")
            with open(json_path, "w") as f:
                json.dump(content, f)

            build_resume(json_path, pdf_path)

            c = Canvas(pdf_path)
            assert c.getPageNumber() == 1

    def test_validation_error_exits_early(self):
        import pytest

        from resumebuilder.schema import validate

        data = make_minimal_content()
        data["education"] = []
        with pytest.raises(ValueError, match='ERROR.*education.*empty'):
            validate(data)

    def test_custom_output_filename(self):
        content = make_full_content()
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "content.json")
            pdf_path = os.path.join(tmpdir, "my_resume.pdf")
            with open(json_path, "w") as f:
                json.dump(content, f)

            build_resume(json_path, pdf_path)
            assert os.path.isfile(pdf_path)
