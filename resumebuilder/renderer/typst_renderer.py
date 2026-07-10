"""Jinja2-based Typst template renderer."""

import copy
import functools
import pathlib
import re

from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = pathlib.Path(__file__).parent / "templates" / "typst"

SECTION_KEYS = {"education", "experience", "projects", "skills", "achievements"}


@functools.lru_cache(maxsize=1)
def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def _render(name: str, **kwargs) -> str:
    return _env().get_template(name).render(**kwargs)


def _esc(s: str) -> str:
    """Escape characters that break Typst 0.15 parser in content."""
    # _ after non-letter triggers unclosed delimiter
    s = re.sub(r"([^a-zA-Z])_([a-zA-Z])", r"\1\2", s)
    # @ and % trigger label resolution and comments
    s = s.replace("@", "\\@").replace("%", "\\%")
    # * anywhere inside #text[] content triggers strong-emphasis parsing bugs
    s = s.replace("*", "\u2217")
    return s.replace("*", "\\*")


def _escape_recursive(obj):
    if isinstance(obj, str):
        return _esc(obj)
    if isinstance(obj, dict):
        return {k: _escape_recursive(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_escape_recursive(x) for x in obj]
    return obj


def _date_str(e: dict) -> str:
    if e.get("date"):
        return e["date"]
    s = e.get("start_date", "")
    e2 = e.get("end_date", "")
    if s and e2:
        return f"{s} – {e2}"
    return s or ""


def generate_typst(data: dict) -> str:
    data = _escape_recursive(copy.deepcopy(data))
    design = data.get("design", {})

    cv = data["cv"]
    connections = []
    if cv.get("email"):
        connections.append(cv["email"])
    if cv.get("phone"):
        connections.append(cv["phone"])
    if cv.get("location"):
        connections.append(cv["location"])
    for sn in (cv.get("social_networks") or []):
        connections.append(f"{sn['network']}: {sn['username']}")
    cv["_connections"] = connections

    preamble = _render("Preamble.j2.typ", design=design)
    header = _render("Header.j2.typ", cv=cv, design=design)
    parts = [preamble, header]

    titles = {"education": "Education", "experience": "Experience",
              "projects": "Projects", "skills": "Skills",
              "achievements": "Achievements"}

    template_names = {
        "education": "entries/EducationEntry.j2.typ",
        "experience": "entries/ExperienceEntry.j2.typ",
        "projects": "entries/NormalEntry.j2.typ",
        "skills": "entries/OneLineEntry.j2.typ",
        "achievements": "entries/BulletEntry.j2.typ",
    }

    for key, title in titles.items():
        entries = data.get(key, [])
        if not entries:
            continue
        parts.append(_render("SectionBeginning.j2.typ",
                              section_title=title, design=design))
        tmpl = template_names[key]
        for e in entries:
            e["date"] = _date_str(e)
            parts.append(_render(tmpl, entry=e, design=design))
        parts.append(_render("SectionEnding.j2.typ"))

    return "\n".join(parts)
