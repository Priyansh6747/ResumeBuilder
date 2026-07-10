import copy

from resumebuilder.measure import measure_total_height


def make_content(experience_bullets=0, project_bullets=0, achievements=0):
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
        "experience": (
            [
                {
                    "title": "SWE",
                    "org": "Co",
                    "dates": "2024–present",
                    "bullets": [
                        {"text": f"bullet {i}", "priority": 1}
                        for i in range(experience_bullets)
                    ],
                }
            ]
            if experience_bullets > 0
            else []
        ),
        "projects": (
            [
                {
                    "name": "Proj",
                    "stack": "Python",
                    "dates": "2025",
                    "bullets": [
                        {"text": f"pb {i}", "priority": 1}
                        for i in range(project_bullets)
                    ],
                }
            ]
            if project_bullets > 0
            else []
        ),
        "skills": [
            {"category": "Lang", "items": "Python, Rust, TypeScript, C"},
        ],
        "achievements": (
            [
                {"text": f"achievement {i}", "priority": 1}
                for i in range(achievements)
            ]
            if achievements > 0
            else []
        ),
    }


class TestMeasure:
    def test_monotonic_in_bullet_count(self):
        h1 = measure_total_height(make_content(experience_bullets=1), 9.5, 400)
        h2 = measure_total_height(make_content(experience_bullets=3), 9.5, 400)
        assert h1 < h2

    def test_height_shrinks_with_font_size(self):
        content = make_content(experience_bullets=2, project_bullets=2, achievements=1)
        h_big = measure_total_height(content, 9.5, 400)
        h_small = measure_total_height(content, 8.0, 400)
        assert h_small < h_big

    def test_deterministic(self):
        content = make_content(experience_bullets=2, project_bullets=1)
        h1 = measure_total_height(content, 9.5, 400)
        h2 = measure_total_height(content, 9.5, 400)
        assert h1 == h2

    def test_no_mutation(self):
        content = make_content(experience_bullets=2)
        original = copy.deepcopy(content)
        measure_total_height(content, 9.5, 400)
        assert content == original
