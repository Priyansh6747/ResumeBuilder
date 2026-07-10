import os
from unittest.mock import patch

import pytest

from resumebuilder.schema import ResumeContent, validate


def make_minimal():
    return {
        "has_photo": False,
        "header": {
            "name": "Test User",
            "phone": "555-0000",
            "email": "test@example.com",
            "linkedin": "linkedin.com/in/test",
            "github": "github.com/test",
            "tagline": "A test user",
        },
        "education": [
            {
                "institution": "Test U",
                "location": "Testville",
                "degree": "BSc Testing",
                "dates": "2020 – 2024",
            }
        ],
        "experience": [],
        "projects": [],
        "skills": [
            {"category": "Languages", "items": "Python, Rust, TypeScript"}
        ],
        "achievements": [],
    }


class TestValidation:
    def test_valid_minimal_parses(self):
        data = make_minimal()
        model = ResumeContent.model_validate(data)
        assert model.header.name == "Test User"
        assert len(model.education) == 1

    def test_education_empty_raises(self):
        data = make_minimal()
        data["education"] = []
        with pytest.raises(ValueError, match='ERROR: "education" section is empty'):
            ResumeContent.model_validate(data)

    def test_skills_empty_raises(self):
        data = make_minimal()
        data["skills"] = []
        with pytest.raises(ValueError, match='ERROR: "skills" section is empty'):
            ResumeContent.model_validate(data)

    def test_missing_priority_experience(self):
        data = make_minimal()
        data["experience"] = [
            {
                "title": "SWE",
                "org": "Co",
                "dates": "2024–present",
                "bullets": [
                    {"text": "Did stuff", "priority": 1},
                    {"text": "Missing priority"},
                ],
            }
        ]
        with pytest.raises(ValueError) as exc:
            validate(data)
        assert str(exc.value) == (
            'ERROR: experience[0].bullets[1] missing required field "priority"'
        )

    def test_missing_priority_projects(self):
        data = make_minimal()
        data["projects"] = [
            {
                "name": "Proj",
                "stack": "Python",
                "dates": "2024",
                "bullets": [
                    {"text": "No prio"},
                ],
            }
        ]
        with pytest.raises(ValueError) as exc:
            validate(data)
        assert str(exc.value) == (
            'ERROR: projects[0].bullets[0] missing required field "priority"'
        )

    def test_missing_priority_achievements(self):
        data = make_minimal()
        data["achievements"] = [
            {"text": "Won award", "priority": 1},
            {"text": "Missing prio"},
        ]
        with pytest.raises(ValueError) as exc:
            validate(data)
        assert str(exc.value) == (
            'ERROR: achievements[1] missing required field "priority"'
        )

    def test_priority_out_of_range(self):
        data = make_minimal()
        data["projects"] = [
            {
                "name": "P",
                "stack": "X",
                "dates": "2024",
                "bullets": [
                    {"text": "bad", "priority": 5},
                ],
            }
        ]
        with pytest.raises(ValueError) as exc:
            validate(data)
        assert str(exc.value) == (
            "ERROR: projects[0].bullets[0].priority must be 1, 2, or 3 (got 5)"
        )

    def test_achievement_priority_out_of_range(self):
        data = make_minimal()
        data["achievements"] = [
            {"text": "bad", "priority": 0},
        ]
        with pytest.raises(ValueError) as exc:
            validate(data)
        assert str(exc.value) == (
            "ERROR: achievements[0].priority must be 1, 2, or 3 (got 0)"
        )

    def test_has_photo_missing_file(self):
        data = make_minimal()
        data["has_photo"] = True
        with patch.object(
            os.path, "isfile", return_value=False
        ):
            with pytest.raises(ValueError) as exc:
                validate(data)
            assert "has_photo is true but no file found" in str(exc.value)

    def test_has_photo_file_exists(self):
        data = make_minimal()
        data["has_photo"] = True
        with patch.object(os.path, "isfile", return_value=True):
            model = ResumeContent.model_validate(data)
            assert model.has_photo is True

    def test_valid_with_experience_and_projects(self):
        data = make_minimal()
        data["experience"] = [
            {
                "title": "SWE",
                "org": "Foo",
                "dates": "2025–present",
                "bullets": [
                    {"text": "Built things", "priority": 1},
                    {"text": "Shipped", "priority": 2},
                ],
            }
        ]
        data["projects"] = [
            {
                "name": "Proj",
                "stack": "Rust",
                "dates": "2025",
                "bullets": [
                    {"text": "Wrote code", "priority": 1},
                ],
            }
        ]
        data["achievements"] = [
            {"text": "Award", "priority": 2},
        ]
        model = ResumeContent.model_validate(data)
        assert len(model.experience[0].bullets) == 2
        assert model.achievements[0].priority == 2
