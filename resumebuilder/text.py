from reportlab.pdfbase.pdfmetrics import stringWidth

from resumebuilder.template import FONT_NAME


def wrap_text(text, font_size, max_width):
    if not text:
        return []
    words = text.split()
    lines = []
    current = ""
    for w in words:
        trial = f"{current} {w}".strip()
        if stringWidth(trial, FONT_NAME, font_size) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines
