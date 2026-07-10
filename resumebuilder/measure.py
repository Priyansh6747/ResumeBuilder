from resumebuilder.template import (
    BULLET_INDENT,
    ENTRY_ROW_HEIGHT,
    HEADER_HEIGHT_FIXED,
    SECTION_HEADER_HEIGHT,
)
from resumebuilder.text import wrap_text


def _leading(font_size):
    return font_size * 1.3


def measure_bullet_height(text, font_size, content_width):
    lines = wrap_text(text, font_size, content_width - BULLET_INDENT)
    return len(lines) * _leading(font_size)


def measure_skills_height(skills, font_size, content_width):
    h = 0
    for skill in skills:
        line = f"{skill['category']}: {skill['items']}"
        lines = wrap_text(line, font_size, content_width)
        h += len(lines) * _leading(font_size)
    return h


def measure_total_height(content, font_size, content_width):
    h = HEADER_HEIGHT_FIXED

    for section_name in ("education", "experience", "projects"):
        entries = content.get(section_name, [])
        h += SECTION_HEADER_HEIGHT
        for entry in entries:
            h += ENTRY_ROW_HEIGHT
            for b in entry.get("bullets", []):
                h += measure_bullet_height(b["text"], font_size, content_width)

    h += SECTION_HEADER_HEIGHT + measure_skills_height(
        content.get("skills", []), font_size, content_width
    )
    h += SECTION_HEADER_HEIGHT
    for a in content.get("achievements", []):
        h += measure_bullet_height(a["text"], font_size, content_width)

    return h
