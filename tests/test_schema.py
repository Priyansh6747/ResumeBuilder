
import pydantic
import pytest

from resumebuilder.schema.models import ResumeContent


def make_minimal():
    return {
        "cv": {
            "name": "Test User",
            "headline": "Engineer",
            "email": "test@example.com",
            "phone": "555-0000",
        },
        "education": [
            {
                "institution": "Test U",
                "area": "Computer Science",
                "degree": "BSc",
                "start_date": "2020",
                "end_date": "2024",
            }
        ],
        "skills": [
            {"label": "Languages", "details": "Python, Rust"}
        ],
    }


def make_full():
    data = make_minimal()
    data["experience"] = [
        {
            "company": "Co",
            "position": "SWE",
            "start_date": "2024",
            "end_date": "present",
            "highlights": ["Built things", "Shipped features"],
        }
    ]
    data["projects"] = [
        {
            "name": "Proj",
            "start_date": "2025",
            "end_date": "2025",
            "summary": "A project",
            "highlights": ["Wrote code"],
        }
    ]
    data["achievements"] = [
        {"bullet": "Won award"},
        {"bullet": "Published paper"},
    ]
    return data


class TestValidation:
    def test_valid_minimal_parses(self):
        model = ResumeContent.model_validate(make_minimal())
        assert model.cv.name == "Test User"
        assert len(model.education) == 1

    def test_education_empty_fails(self):
        data = make_minimal()
        data["education"] = []
        with pytest.raises(pydantic.ValidationError):
            ResumeContent.model_validate(data)

    def test_skills_empty_fails(self):
        data = make_minimal()
        data["skills"] = []
        with pytest.raises(pydantic.ValidationError):
            ResumeContent.model_validate(data)

    def test_missing_cv_name_fails(self):
        data = make_minimal()
        del data["cv"]["name"]
        with pytest.raises(pydantic.ValidationError):
            ResumeContent.model_validate(data)

    def test_valid_full_parses(self):
        model = ResumeContent.model_validate(make_full())
        assert len(model.experience) == 1
        assert len(model.projects) == 1
        assert len(model.achievements) == 2
        assert model.experience[0].highlights == ["Built things", "Shipped features"]

    def test_photo_missing_raises(self):
        data = make_minimal()
        data["cv"]["photo"] = "/nonexistent/photo.jpg"
        with pytest.raises(ValueError, match="Photo file not found"):
            ResumeContent.model_validate(data)

    def test_photo_present_ok(self, tmp_path):
        data = make_minimal()
        photo = tmp_path / "photo.jpg"
        photo.write_text("fake image")
        data["cv"]["photo"] = str(photo)
        model = ResumeContent.model_validate(data)
        assert model.cv.photo == str(photo)

    def test_valid_content_with_photo_disabled(self):
        data = make_minimal()
        model = ResumeContent.model_validate(data)
        assert model.cv.photo is None
        assert model.cv.name == "Test User"

    def test_social_networks(self):
        data = make_minimal()
        data["cv"]["social_networks"] = [
            {"network": "LinkedIn", "username": "test"},
            {"network": "GitHub", "username": "testuser"},
        ]
        model = ResumeContent.model_validate(data)
        assert len(model.cv.social_networks) == 2
        assert model.cv.social_networks[0].network == "LinkedIn"
