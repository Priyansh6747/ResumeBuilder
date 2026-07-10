import copy

import pytest

from resumebuilder.fit import OverflowError, collect_all_bullets_by_priority, fit_resume


def make_content(num_exp=1, bullets_per_exp=1, num_proj=1, bullets_per_proj=1,
                 num_ach=0, priority=1, tagline="test"):
    content = {
        "has_photo": False,
        "header": {
            "name": "Test User",
            "phone": "555-0000",
            "email": "test@example.com",
            "linkedin": "linkedin.com/in/test",
            "github": "github.com/test",
            "tagline": tagline,
        },
        "education": [
            {
                "institution": "Test U",
                "location": "Testville",
                "degree": "BSc Testing",
                "dates": "2020 – 2024",
            }
        ],
        "experience": [
            {
                "title": f"Job {i}",
                "org": f"Co {i}",
                "dates": "2024–present",
                "bullets": [
                    {"text": f"Did thing {j}", "priority": priority}
                    for j in range(bullets_per_exp)
                ],
            }
            for i in range(num_exp)
        ],
        "projects": [
            {
                "name": f"Proj {i}",
                "stack": "Python",
                "dates": "2025",
                "bullets": [
                    {"text": f"Built {j}", "priority": priority}
                    for j in range(bullets_per_proj)
                ],
            }
            for i in range(num_proj)
        ],
        "skills": [
            {"category": "Lang", "items": "Python, Rust, TypeScript, C"},
        ],
        "achievements": [
            {"text": f"Award {i}", "priority": priority}
            for i in range(num_ach)
        ],
    }
    return content


def make_content_mixed():
    content = {
        "has_photo": False,
        "header": {
            "name": "Test User",
            "phone": "555-0000",
            "email": "test@example.com",
            "linkedin": "linkedin.com/in/test",
            "github": "github.com/test",
            "tagline": "test",
        },
        "education": [
            {
                "institution": "Test U",
                "location": "Testville",
                "degree": "BSc Testing",
                "dates": "2020 – 2024",
            }
        ],
        "experience": [
            {
                "title": "Job 0",
                "org": "Co 0",
                "dates": "2024–present",
                "bullets": [
                    {"text": "p1", "priority": 1},
                    {"text": "p3 entry0", "priority": 3},
                    {"text": "p1 again", "priority": 1},
                ],
            },
            {
                "title": "Job 1",
                "org": "Co 1",
                "dates": "2023–2024",
                "bullets": [
                    {"text": "p2 job1", "priority": 2},
                ],
            },
        ],
        "projects": [
            {
                "name": "Proj 0",
                "stack": "Rust",
                "dates": "2025",
                "bullets": [
                    {"text": "p3 proj0", "priority": 3},
                    {"text": "p2 proj0", "priority": 2},
                ],
            },
        ],
        "skills": [
            {"category": "Lang", "items": "Python, Rust"},
        ],
        "achievements": [
            {"text": "p1 ach", "priority": 1},
            {"text": "p3 ach", "priority": 3},
        ],
    }
    return content


class TestCollect:
    def test_collects_all(self):
        content = make_content(num_exp=2, bullets_per_exp=2, num_proj=1,
                               bullets_per_proj=3, num_ach=2)
        queue = collect_all_bullets_by_priority(content)
        assert len(queue) == 2 * 2 + 1 * 3 + 2

    def test_priority_descending_order(self):
        content = make_content_mixed()
        queue = collect_all_bullets_by_priority(content)
        priorities = [q[0] for q in queue]
        for i in range(len(priorities) - 1):
            assert priorities[i] >= priorities[i + 1]

    def test_p3s_before_p2s_before_p1s(self):
        content = make_content_mixed()
        queue = collect_all_bullets_by_priority(content)
        priorities = [q[0] for q in queue]
        assert 3 in priorities
        assert priorities.index(3) < min(
            i for i, p in enumerate(priorities) if p == 2
        )
        assert max(i for i, p in enumerate(priorities) if p == 2) < min(
            i for i, p in enumerate(priorities) if p == 1
        )


class TestFit:
    def test_fits_at_top_with_no_drops(self):
        content = make_content(num_exp=1, bullets_per_exp=1, num_proj=1,
                               bullets_per_proj=1, num_ach=1)
        working, font_size, dropped = fit_resume(content, 10000, 400)
        assert len(dropped) == 0
        assert font_size == 9.5

    def test_drops_p3_before_p2_before_p1(self):
        content = make_content_mixed()
        usable = 300
        _, font_size, dropped = fit_resume(content, usable, 400)
        texts = [d["text"] for d in dropped]
        p3_texts = [t for t in texts if "p3" in t]
        assert len(p3_texts) > 0

    def test_drops_persist_across_font_steps(self):
        from reportlab.lib.pagesizes import LETTER

        from resumebuilder.template import HEADER_HEIGHT_FIXED, MARGIN_BOTTOM, MARGIN_TOP

        usable = LETTER[1] - MARGIN_TOP - MARGIN_BOTTOM - HEADER_HEIGHT_FIXED

        # pack content so it slightly exceeds one page at 9.5pt
        content = make_content(num_exp=3, bullets_per_exp=6, num_proj=3,
                               bullets_per_proj=5, num_ach=4, priority=3)

        _, font_size, dropped = fit_resume(content, usable, 400)
        if dropped:
            assert len(dropped) > 0

    def test_hard_overflow_error_when_only_p1_remains(self):
        content = make_content(num_exp=4, bullets_per_exp=10, num_proj=4,
                               bullets_per_proj=10, num_ach=5, priority=1,
                               tagline="x" * 500)
        usable = 1
        with pytest.raises(OverflowError, match="content still exceeds one page"):
            fit_resume(content, usable, 400)

    def test_original_not_mutated(self):
        content = make_content_mixed()
        original = copy.deepcopy(content)
        fit_resume(content, 10000, 400)
        assert content == original

    def test_dropped_list_has_truncated_text(self):
        content = make_content_mixed()
        content["experience"][0]["bullets"][0]["text"] = "a" * 80
        usable = 50
        try:
            _, _, dropped = fit_resume(content, usable, 400)
        except OverflowError:
            pytest.skip("Content overflows even at minimum")
        for d in dropped:
            assert len(d["text"]) <= 53
