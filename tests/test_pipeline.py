import os
import tempfile

import pytest

from resumebuilder.renderer.compiler import compile_typst
from resumebuilder.renderer.typst_renderer import generate_typst
from resumebuilder.schema import ReadError, read_yaml
from resumebuilder.schema.models import ResumeContent


def make_content():
    return {
        "cv": {
            "name": "Test User",
            "email": "test@example.com",
        },
        "education": [
            {
                "institution": "University",
                "area": "CS",
                "degree": "BSc",
                "start_date": "2020",
                "end_date": "2024",
            }
        ],
        "experience": [
            {
                "company": "Acme",
                "position": "Engineer",
                "start_date": "2024",
                "end_date": "present",
                "highlights": ["Built things"],
            }
        ],
        "skills": [{"label": "Lang", "details": "Python"}],
    }


class TestPipeline:
    def test_end_to_end_yaml_to_pdf(self):
        content = make_content()
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_path = os.path.join(tmpdir, "cv.yaml")
            pdf_path = os.path.join(tmpdir, "output.pdf")
            import ruamel.yaml
            yaml = ruamel.yaml.YAML()
            with open(yaml_path, "w") as f:
                yaml.dump(content, f)

            from resumebuilder.pipeline import build_resume
            build_resume(yaml_path, pdf_path)

            assert os.path.isfile(pdf_path)
            assert os.path.getsize(pdf_path) > 0

    def test_typst_source_generation(self):
        content = make_content()
        model = ResumeContent.model_validate(content)
        src = generate_typst(model.model_dump())
        assert "#set page" in src
        assert "#set text" in src
        assert "Test User" in src
        assert "Acme" in src
        assert "Built things" in src
        assert "Python" in src

    def test_typst_compiles_to_pdf(self):
        content = make_content()
        model = ResumeContent.model_validate(content)
        src = generate_typst(model.model_dump())
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "output.pdf")
            compile_typst(src, pdf_path)
            assert os.path.isfile(pdf_path)
            assert os.path.getsize(pdf_path) > 0


class TestYamlReader:
    def test_read_yaml_file(self, tmp_path):
        import ruamel.yaml
        yaml = ruamel.yaml.YAML()
        p = tmp_path / "test.yaml"
        content = {"cv": {"name": "Test"}}
        with open(p, "w") as f:
            yaml.dump(content, f)

        result = read_yaml(p)
        assert result["cv"]["name"] == "Test"

    def test_read_missing_file_raises(self, tmp_path):
        p = tmp_path / "nonexistent.yaml"
        with pytest.raises(ReadError, match="doesn't exist"):
            read_yaml(p)

    def test_read_empty_string_raises(self):
        with pytest.raises(ReadError, match="empty"):
            read_yaml("")
