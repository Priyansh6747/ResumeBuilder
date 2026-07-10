"""Typst source generator — user content via #raw blocks to avoid parser bugs."""
import copy
import re


def _date_str(entry: dict) -> str:
    if entry.get("date"):
        return entry["date"]
    if entry.get("start_date") and entry.get("end_date"):
        return f"{entry['start_date']} – {entry['end_date']}"
    if entry.get("start_date"):
        return entry["start_date"]
    return ""


def _esc(s: str) -> str:
    """Escape special chars that Typst 0.15 can't parse even in code-mode #text[]. """
    s = re.sub(r'([^a-zA-Z])_([a-zA-Z])', r'\1\2', s)
    # Typst: @ resolves to label, % starts comment, * is strong emphasis
    return s.replace("@", "\\@").replace("%", "\\%").replace("*", "\\*")


def generate_typst(data: dict) -> str:
    data = copy.deepcopy(data)
    lines = []
    w = lines.append

    w(
        '#set page(paper: "us-letter", margin: '
        "(top: 0.50in, bottom: 0.50in, left: 0.60in, right: 0.60in))"
    )
    w('#set text(font: "Times New Roman", size: 9.5pt)')
    w("")

    cv = data["cv"]
    w(f'#text(size: 22pt, weight: "bold")[{_esc(cv["name"])}]')
    if cv.get("headline"):
        w(f'#text(size: 9.5pt)[{_esc(cv["headline"])}]')
    contacts = []
    if cv.get("email"):
        contacts.append(_esc(cv["email"]))
    if cv.get("phone"):
        contacts.append(cv["phone"])
    for sn in (cv.get("social_networks") or []):
        contacts.append(f"{sn['network']}: {sn['username']}")
    if contacts:
        w(f'#text(size: 9.5pt)[{"  |  ".join(contacts)}]')

    def section_header(title):
        w("")
        w("#v(0.30cm)")
        w(f'#text(size: 10.5pt, weight: "bold", tracking: 0.8pt)[{title.upper()}]')
        w("#v(0.06cm)")
        w('#line(stroke: 0.6pt, length: 100%)')
        w("#v(0.10cm)")

    for key, title in [("education", "Education"), ("experience", "Experience"),
                        ("projects", "Projects"), ("skills", "Skills"),
                        ("achievements", "Achievements")]:
        items = data.get(key, [])
        if not items:
            continue
        section_header(title)

        for e in items:
            date = _date_str(e)

            if key == "education":
                w(f'#text(weight: "bold")[{_esc(e["institution"])}]')
                extra = _esc(e.get("area", ""))
                if e.get("degree"):
                    extra += f"  |  Degree: {e['degree']}"
                if date:
                    extra += f"  |  {date}"
                w(f'#text(size: 9.5pt)[{extra}]')
                for h in (e.get("highlights") or []):
                    w(f'#text(size: 9.5pt)[  \u2022  {_esc(h)}]')
                w("#v(0.15cm)")

            elif key == "experience":
                w(
                    f'#text(weight: "bold", size: 10pt)[{_esc(e["company"])}]'
                    f'  #text(style: "italic", size: 9.5pt)[{_esc(e["position"])}]'
                    f'  #text(size: 10pt)[{date}]'
                )
                if e.get("summary"):
                    w(f'#text(size: 9.5pt)[{_esc(e["summary"])}]')
                for h in (e.get("highlights") or []):
                    w(f'#text(size: 9.5pt)[  \u2022  {_esc(h)}]')
                w("#v(0.15cm)")

            elif key == "projects":
                w(
                    f'#text(weight: "bold", size: 10pt)[{_esc(e["name"])}]'
                    f'  #text(size: 10pt)[{date}]'
                )
                if e.get("summary"):
                    w(f'#text(size: 9.5pt)[{_esc(e["summary"])}]')
                for h in (e.get("highlights") or []):
                    w(f'#text(size: 9.5pt)[  \u2022  {_esc(h)}]')
                w("#v(0.15cm)")

            elif key == "skills":
                w(f'#text(weight: "bold")[{_esc(e["label"])}:]  #text[{_esc(e["details"])}]')

            elif key == "achievements":
                w(f'#text(size: 9.5pt)[  \u2022  {_esc(e["bullet"])}]')

    return "\n".join(lines)
