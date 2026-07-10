import json

from reportlab.pdfgen import canvas

from resumebuilder.draw import (
    draw_achievements_section,
    draw_education_section,
    draw_experience_section,
    draw_header,
    draw_projects_section,
    draw_skills_section,
)
from resumebuilder.fit import fit_resume
from resumebuilder.schema import validate
from resumebuilder.template import (
    HEADER_HEIGHT_FIXED,
    MARGIN_BOTTOM,
    MARGIN_SIDE,
    MARGIN_TOP,
    PAGE_SIZE,
)


def _report(dropped, font_size, out_path):
    if dropped:
        print(f"WARN: fit at {font_size}pt after dropping {len(dropped)} low-priority bullets:")
        for d in dropped:
            print(f"  - {d['section']}[{d['entry_idx']}] bullet: \"{d['text']}\"")
    print(f"OK: rendered {out_path} (1 page, {font_size}pt)")


def build_resume(content_path, out_path="resume_draft.pdf"):
    with open(content_path) as f:
        data = json.load(f)

    validate(data)

    page_width, page_height_full = PAGE_SIZE
    content_width = page_width - 2 * MARGIN_SIDE
    usable_height = page_height_full - MARGIN_TOP - MARGIN_BOTTOM - HEADER_HEIGHT_FIXED

    fitted, font_size, dropped = fit_resume(data, usable_height, content_width)

    c = canvas.Canvas(out_path, pagesize=PAGE_SIZE)
    y = draw_header(
        c, fitted["header"], fitted["has_photo"], page_height_full, page_width
    )
    y = draw_education_section(c, fitted["education"], font_size, y, content_width)
    y = draw_experience_section(c, fitted["experience"], font_size, y, content_width)
    y = draw_projects_section(c, fitted["projects"], font_size, y, content_width)
    y = draw_skills_section(c, fitted["skills"], font_size, y, content_width)
    draw_achievements_section(c, fitted["achievements"], font_size, y, content_width)
    c.save()

    _report(dropped, font_size, out_path)
