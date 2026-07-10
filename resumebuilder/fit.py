import copy

from resumebuilder.measure import measure_total_height
from resumebuilder.template import FONT_SIZE_LADDER


class OverflowError(Exception):
    pass


def _truncate(text, max_chars=50):
    if len(text) <= max_chars + 3:
        return text
    return text[:max_chars] + "..."


def collect_all_bullets_by_priority(content):
    candidates = []
    for section in ("experience", "projects"):
        entries = content[section]
        for entry_idx in reversed(range(len(entries))):
            bullets = entries[entry_idx]["bullets"]
            for bullet_idx in reversed(range(len(bullets))):
                prio = bullets[bullet_idx].get("priority", 1)
                candidates.append((prio, section, entry_idx, bullet_idx))
    for idx in reversed(range(len(content["achievements"]))):
        prio = content["achievements"][idx].get("priority", 1)
        candidates.append((prio, "achievements", idx, None))
    return sorted(candidates, key=lambda c: -c[0])


def _drop_bullet(working, section_name, entry_idx, bullet_idx):
    if section_name == "achievements":
        del working[section_name][entry_idx]
    else:
        del working[section_name][entry_idx]["bullets"][bullet_idx]


def _bullet_text(working, section_name, entry_idx, bullet_idx):
    if section_name == "achievements":
        return working[section_name][entry_idx]["text"]
    return working[section_name][entry_idx]["bullets"][bullet_idx]["text"]


def fit_resume(content, usable_height, content_width):
    dropped = []
    working = copy.deepcopy(content)

    for font_size in FONT_SIZE_LADDER:
        while True:
            height = measure_total_height(working, font_size, content_width)
            if height <= usable_height:
                return working, font_size, dropped

            queue = collect_all_bullets_by_priority(working)
            if not queue:
                break

            _, section, entry_idx, bullet_idx = queue[0]
            text = _bullet_text(working, section, entry_idx, bullet_idx)
            dropped.append(
                {"text": _truncate(text), "section": section, "entry_idx": entry_idx}
            )
            _drop_bullet(working, section, entry_idx, bullet_idx)

    remaining_prio1 = 0
    for s in ("experience", "projects"):
        for entry in working[s]:
            for b in entry.get("bullets", []):
                if b.get("priority") == 1:
                    remaining_prio1 += 1
    for a in working["achievements"]:
        if a.get("priority") == 1:
            remaining_prio1 += 1

    raise OverflowError(
        f"ERROR: content still exceeds one page at {FONT_SIZE_LADDER[-1]}pt "
        f"even after dropping {len(dropped)} bullets "
        f"({remaining_prio1} priority-1 bullets remain, cannot drop further). "
        f"Cut at least 1 more bullet or shorten a bullet's text, then retry."
    )
