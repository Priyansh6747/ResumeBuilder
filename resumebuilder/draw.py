import os
import tempfile

from PIL import Image, ImageDraw
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth

from resumebuilder.template import (
    ACHIEVEMENTS_HEADER,
    BULLET_INDENT,
    EDUCATION_SECTION_NAME,
    ENTRY_GAP_AFTER,
    ENTRY_TITLE_SIZE,
    EXPERIENCE_SECTION_NAME,
    FONT_NAME,
    FONT_NAME_BOLD,
    FONT_NAME_ITALIC,
    HEADER_SECTION_GAP,
    MARGIN_SIDE,
    MARGIN_TOP,
    NAME_SIZE,
    PHOTO_DIAMETER,
    PROJECTS_SECTION_NAME,
    RULE_COLOR,
    SECTION_GAP_AFTER,
    SECTION_SIZE,
    SKILLS_SECTION_NAME,
    TAGLINE_SIZE,
    TEXT_COLOR,
)
from resumebuilder.text import wrap_text


def _leading(font_size):
    return font_size * 1.3


def _y_bottom(margin_bottom):
    return margin_bottom


def make_circular_photo(src_path, out_path, size_px=340):
    img = Image.open(os.path.expanduser(src_path)).convert("RGBA").resize((size_px, size_px))
    mask = Image.new("L", (size_px, size_px), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size_px, size_px), fill=255)
    img.putalpha(mask)
    img.save(out_path)
    return out_path


def draw_header(c, header, has_photo, page_height, page_width):
    y = page_height - MARGIN_TOP

    content_width = page_width - 2 * MARGIN_SIDE
    text_content_width = content_width
    x = MARGIN_SIDE

    if has_photo:
        text_content_width = content_width - PHOTO_DIAMETER - 0.2 * inch

    c.setFont(FONT_NAME_BOLD, NAME_SIZE)
    c.setFillColor(TEXT_COLOR)
    c.drawString(x, y - NAME_SIZE, header["name"])
    y -= NAME_SIZE + _leading(NAME_SIZE) * 0.3

    c.setFont(FONT_NAME, TAGLINE_SIZE)
    c.drawString(x, y - TAGLINE_SIZE, header.get("tagline", ""))
    y -= TAGLINE_SIZE + _leading(TAGLINE_SIZE) * 0.3

    contact_line = (
        f"{header['phone']}  |  {header['email']}"
        f"  |  {header['linkedin']}  |  {header['github']}"
    )
    c.setFont(FONT_NAME, TAGLINE_SIZE)
    c.drawString(x, y - TAGLINE_SIZE, contact_line)
    y -= TAGLINE_SIZE + HEADER_SECTION_GAP

    if has_photo:
        photo_path = os.path.expanduser("~/resume_photo.jpg")
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp.close()
        make_circular_photo(photo_path, tmp.name)
        px = MARGIN_SIDE + text_content_width + 0.2 * inch
        py = page_height - MARGIN_TOP - PHOTO_DIAMETER
        c.drawImage(tmp.name, px, py, width=PHOTO_DIAMETER, height=PHOTO_DIAMETER, mask="auto")
        os.unlink(tmp.name)

    return y


def draw_section_header(c, text, y, content_width, font_size):
    c.setFont(FONT_NAME_BOLD, SECTION_SIZE)
    c.setFillColor(TEXT_COLOR)
    c.drawString(MARGIN_SIDE, y, text.upper())
    y -= SECTION_SIZE * 1.3 + 1

    c.setStrokeColor(RULE_COLOR)
    c.setLineWidth(0.6)
    c.line(MARGIN_SIDE, y, MARGIN_SIDE + content_width, y)
    y -= SECTION_GAP_AFTER + 4

    return y


def draw_entry_row(c, title, subtitle, dates, y, content_width, font_size):
    content_col_right = MARGIN_SIDE + content_width

    c.setFont(FONT_NAME_BOLD, ENTRY_TITLE_SIZE)
    c.drawString(MARGIN_SIDE, y, title)

    if subtitle:
        sw = stringWidth(title, FONT_NAME_BOLD, ENTRY_TITLE_SIZE)
        sep_width = stringWidth("  |  ", FONT_NAME, ENTRY_TITLE_SIZE)
        c.setFont(FONT_NAME_ITALIC, ENTRY_TITLE_SIZE - 0.5)
        c.drawString(MARGIN_SIDE + sw + sep_width, y, subtitle)

    if dates:
        c.setFont(FONT_NAME, ENTRY_TITLE_SIZE)
        c.drawRightString(content_col_right, y, dates)

    y -= ENTRY_TITLE_SIZE * 1.4 + ENTRY_GAP_AFTER
    return y


def draw_bullets(c, bullets, y, content_width, font_size):
    for b in bullets:
        lines = wrap_text(b["text"], font_size, content_width - BULLET_INDENT)
        for line in lines:
            c.setFont(FONT_NAME, font_size)
            c.drawString(MARGIN_SIDE + BULLET_INDENT, y, line)
            bullet_x = MARGIN_SIDE + BULLET_INDENT - stringWidth("•  ", FONT_NAME, font_size)
            c.drawString(bullet_x, y, "•")
            y -= _leading(font_size)
    return y


def draw_education_section(c, entries, font_size, y, content_width):
    y = draw_section_header(c, EDUCATION_SECTION_NAME, y, content_width, font_size)
    for entry in entries:
        c.setFont(FONT_NAME_BOLD, font_size)
        c.drawString(MARGIN_SIDE, y, entry["institution"])
        y -= _leading(font_size)

        c.setFont(FONT_NAME, font_size)
        line = f"{entry['degree']}  |  {entry['dates']}  |  {entry['location']}"
        c.drawString(MARGIN_SIDE + BULLET_INDENT, y, line)
        y -= _leading(font_size) + 4
    return y


def draw_experience_section(c, entries, font_size, y, content_width):
    y = draw_section_header(c, EXPERIENCE_SECTION_NAME, y, content_width, font_size)
    for entry in entries:
        y = draw_entry_row(c, entry["title"], entry["org"], entry["dates"],
                           y, content_width, font_size)
        if entry.get("bullets"):
            y = draw_bullets(c, entry["bullets"], y, content_width, font_size)
    return y


def draw_projects_section(c, entries, font_size, y, content_width):
    y = draw_section_header(c, PROJECTS_SECTION_NAME, y, content_width, font_size)
    for entry in entries:
        y = draw_entry_row(c, entry["name"], entry["stack"], entry["dates"],
                           y, content_width, font_size)
        if entry.get("bullets"):
            y = draw_bullets(c, entry["bullets"], y, content_width, font_size)
    return y


def draw_skills_section(c, skills, font_size, y, content_width):
    y = draw_section_header(c, SKILLS_SECTION_NAME, y, content_width, font_size)
    for skill in skills:
        line = f"{skill['category']}: {skill['items']}"
        lines = wrap_text(line, font_size, content_width)
        for wrapped_line in lines:
            c.setFont(FONT_NAME_BOLD, font_size)
            c.drawString(MARGIN_SIDE, y, wrapped_line)
            y -= _leading(font_size)
    return y


def draw_achievements_section(c, achievements, font_size, y, content_width):
    y = draw_section_header(c, ACHIEVEMENTS_HEADER, y, content_width, font_size)
    for a in achievements:
        lines = wrap_text(a["text"], font_size, content_width - BULLET_INDENT)
        for line in lines:
            c.setFont(FONT_NAME, font_size)
            c.drawString(MARGIN_SIDE + BULLET_INDENT, y, line)
            bullet_x = MARGIN_SIDE + BULLET_INDENT - stringWidth("•  ", FONT_NAME, font_size)
            c.drawString(bullet_x, y, "•")
            y -= _leading(font_size)
    return y
