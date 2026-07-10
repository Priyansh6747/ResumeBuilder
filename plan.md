# Resume Builder — Implementation Plan

> Personal-use skill that renders a **fully-decided** resume (content + ordering + bullet
> priority already chosen by the agent) into a **pixel-perfect one-page PDF** matching a fixed
> personal template. The skill owns 100% of visual formatting; the agent owns 100% of content.

---

## 1. Goals & Non-Goals

### Goals
1. Render `content.json` → `resume_draft.pdf` (always that name; "draft" reinforces review).
2. **Always fits one page** — via a deterministic font-size fallback ladder + priority-driven
   bullet trimming. Never silently spills to page 2.
3. **Strict separation of concerns** — the schema exposes *no* font/color/spacing fields. The
   agent can only ever ship text + `priority`.
4. One-line validation errors before any PDF is touched (fail fast, fail loud).
5. Match the locked personal template exactly (Times-Roman, small-caps section headers with
   hairline rules, right-aligned dates, optional circular photo).
6. Report every sacrifice (dropped bullet, font-size step) — silent overflow is a bug.

### Non-Goals
- No multi-page layout — a resume that can't fit at 8pt with only priority-1 content is a
  *content* problem; the engine raises `OverflowError` rather than rendering page 2.
- No agent control over formatting — there is nothing in the schema for it to set.
- No per-run photo path — `has_photo` is a boolean; the photo location is fixed infra config.
- No "themes" — there is exactly one template.
- No JD-tailoring / content selection logic — the agent decides that before writing JSON.

---

## 2. Architecture

```
content.json (agent writes: text + priority only)
        ↓
resumebuilder.pipeline.build_resume()   ← fixed template + fit/overflow engine
        ↓
resume_draft.pdf   (always this name)
```

Single-direction data flow. The fit engine runs a **dry-run measurement pass** before any
real drawing, so layout decisions are made on simulated heights, never on the live canvas.

### Module layout

```
resumebuilder/
├── __init__.py
├── schema.py            # Pydantic models + one-line-error validation contract
├── template.py          # Locked constants (margins, fonts, sizes, ladder, photo)
├── text.py             # wrap_text(), stringWidth-based greedy word-wrap
├── measure.py          # Dry-run height simulation at a given font size
├── fit.py              # Fit/overflow engine: font ladder + priority bullet trimming
├── draw.py             # Drawing primitives (header, sections, entry rows, photo)
├── pipeline.py         # build_resume(): validate → fit → render → report
└── cli.py              # `resume-builder content.json [-o out.pdf]` entry point
tests/
├── test_schema.py
├── test_text.py
├── test_measure.py
├── test_fit.py
└── test_pipeline.py
```

Rationale for separating `measure` from `fit`: measurement is a pure function of
`(content, font_size, width)` and gets its own exhaustive tests; `fit` composes measurements
with the drop queue and is the only module that mutates content.

---

## 3. Dependencies (justification)

| Lib | Why |
|---|---|
| `reportlab>=4.2` | PDF `Canvas`, `LETTER` page size, `inch` units, `stringWidth` for word-wrap & right-alignment. Base14 `Times-Roman` family ships zero-setup — no font registration needed. |
| `Pillow>=10.4` | Reportlab cannot crop to a circle natively. PIL builds an RGBA circular mask → temp PNG → embedded via `drawImage(mask="auto")`. Only used when `has_photo: true`. |
| `pydantic>=2.9` | Models the content schema with type coercion + custom validators that emit the exact one-line error contract (e.g. `ERROR: experience[0].bullets[2] missing required field "priority"`). Cleaner than hand-rolled `isinstance` ladders. |
| `pydantic-core>=2.23` | Pinned alongside pydantic for reproducible Rust-backed validation. |

Dev group: `pytest`, `pytest-cov`, `ruff`. No runtime dep on these.

> **Note:** `os`, `json`, `copy`, `dataclasses` are stdlib and need no declaration.

---

## 4. Content Schema (the *only* agent surface)

Fixed section order — **no** `section_order` field, **no** `custom_section` type in v1.

```
Header → Education → Experience → Projects → Skills → Achievements
```

Top-level fields:

| Field | Type | Rule |
|---|---|---|
| `has_photo` | `bool` | default `false`. `true` ⇒ skill loads fixed `~/resume_photo.jpg` (never a per-run path). |
| `header` | object | `name`, `phone`, `email`, `linkedin`, `github`, `tagline` — all strings, required. |
| `education` | list | ≥1 entry. Each: `institution`, `location`, `degree`, `dates`. |
| `experience` | list | ≥0 entries. Each: `title`, `org`, `dates`, `bullets[]`. |
| `projects` | list | ≥0 entries. Each: `name`, `stack`, `dates`, `bullets[]`. |
| `skills` | list | ≥1. Each: `category`, `items` (single comma-joined string). |
| `achievements` | list | ≥0. Each: `text`, `priority`. |

Every `bullet` (in experience & projects) and every `achievement` carries a mandatory
`priority: int ∈ {1,2,3}`:
- `1` = must-keep
- `2` = droppable before touching priority-1
- `3` = cut first

**Absence of `priority` is a validation error, not a default** — forces the agent to always
think about overflow.

### Validation contract (one-line errors, pre-render)

| Failure | Message |
|---|---|
| Bullet missing `priority` | `ERROR: experience[0].bullets[2] missing required field "priority"` |
| `has_photo: true`, no file | `ERROR: has_photo is true but no file found at ~/resume_photo.jpg` |
| Empty required section | `ERROR: "education" section is empty — at least one entry required` |
| `priority` out of range | `ERROR: projects[1].bullets[0].priority must be 1, 2, or 3 (got 5)` |

Validation runs *before* `Canvas` is constructed — a bad input never produces a partial PDF.

### Array-order semantics
`experience` / `projects` array order **is** the tiebreak signal for overflow trimming — order
entries by actual importance (not chronological), since the same order doubles as a ranking.

Section counts (2 experience / 3–4 projects) are a content *convention*, not hard validation.
The fit engine handles whatever count arrives; wild deviation just triggers more aggressive
trimming or a hard `OverflowError`.

---

## 5. The Locked Template (zero agent input, ever)

```python
PAGE_SIZE        = LETTER
MARGIN_TOP       = 0.5 * inch
MARGIN_BOTTOM    = 0.5 * inch
MARGIN_SIDE      = 0.6 * inch

FONT_NAME        = "Times-Roman"
FONT_NAME_BOLD   = "Times-Bold"
FONT_NAME_ITALIC = "Times-Italic"

NAME_SIZE        = 22
TAGLINE_SIZE     = 9.5
SECTION_SIZE     = 10.5        # pseudo small-caps section headers
ENTRY_TITLE_SIZE = 10
BODY_SIZE        = 9.5         # first rung of the font-size fallback ladder
FONT_SIZE_LADDER = [9.5, 9.0, 8.5, 8.0]   # never below 8pt — illegible below

LINE_LEADING     = 12.5        # at BODY_SIZE=9.5; scales proportionally per ladder step
RULE_COLOR       = "#000000"
TEXT_COLOR       = "#000000"

PHOTO_DIAMETER   = 0.85 * inch
PHOTO_PATH       = "~/resume_photo.jpg"    # fixed infra config, never per-run
```

### Section header
Pseudo small-caps (Base14 has no real small-caps glyphs): render `text.upper()` in
`Times-Bold` at `SECTION_SIZE`, slightly letter-spaced, then a 0.6pt hairline rule under it.

### Entry row (the trickiest primitive)
`title` (bold) left, optional `subtitle` (italic, 0.5pt smaller) inline-right of title, and
`dates` right-aligned against the **content column width** (computed, not a fixed x). Uses
`stringWidth` for the title to position the subtitle, and `drawRightString(x + width, ...)` for
the date.

### Circular photo (only when `has_photo: true`)
PIL preprocessing into a circular-masked temp PNG before embedding:
```python
def make_circular_photo(src_path, out_path, size_px=340):
    img = Image.open(os.path.expanduser(src_path)).convert("RGBA").resize((size_px, size_px))
    mask = Image.new("L", (size_px, size_px), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size_px, size_px), fill=255)
    img.putalpha(mask)
    img.save(out_path)
```
`text_width` only shrinks to make room for the photo when `has_photo` is true — full content
width otherwise. Photo placed at `MARGIN_SIDE + text_width + 0.2*inch`.

---

## 6. Height Measurement (the dry-run pass everything depends on)

Pure functions of `(content, font_size, content_width)` — no side effects, heavily unit-tested.

```python
def wrap_text(text, font, size, max_width):
    """Greedy word-wrap via stringWidth → list of lines."""
    words = text.split()
    lines, current = [], ""
    for w in words:
        trial = f"{current} {w}".strip()
        if stringWidth(trial, font, size) <= max_width:
            current = trial
        else:
            lines.append(current); current = w
    if current:
        lines.append(current)
    return lines

def measure_bullet_height(text, font_size, content_width, bullet_indent=14):
    lines = wrap_text(text, FONT_NAME, font_size, content_width - bullet_indent)
    return len(lines) * (font_size * 1.3)   # leading scales with font size

def measure_total_height(content, font_size, content_width):
    h = HEADER_HEIGHT_FIXED
    for section_name in ("education", "experience", "projects"):
        h += SECTION_HEADER_HEIGHT
        for entry in content[section_name]:
            h += ENTRY_ROW_HEIGHT
            for b in entry.get("bullets", []):
                h += measure_bullet_height(b["text"], font_size, content_width)
    h += SECTION_HEADER_HEIGHT + measure_skills_height(content["skills"], font_size, content_width)
    h += SECTION_HEADER_HEIGHT
    for a in content["achievements"]:
        h += measure_bullet_height(a["text"], font_size, content_width)
    return h
```

`HEADER_HEIGHT_FIXED`, `SECTION_HEADER_HEIGHT`, `ENTRY_ROW_HEIGHT` are computed once in
`template.py` from the locked constants — not magic numbers sprinkled in measure code.

---

## 7. The Fit/Overflow Engine

### Drop-queue ordering (the tiebreak rule)
1. Gather every droppable bullet across `experience`, `projects`, and `achievements`,
   each tagged `(priority, section, entry_idx, bullet_idx)`.
2. Within each section, iterate entries in **reversed** order (lowest-ranked entry = last array
   entry first) and within an entry iterate bullets in **reversed** order (last bullet first —
   agents front-load their strongest point, so the weakest is at the end).
3. Sort the queue by **priority descending** (3s dropped before 2s before 1s), stable within a
   priority group to preserve the reversed-order tiebreak.

```python
def collect_all_bullets_by_priority(content):
    candidates = []
    for section in ("experience", "projects"):
        entries = content[section]
        for entry_idx in reversed(range(len(entries))):
            bullets = entries[entry_idx]["bullets"]
            for bullet_idx in reversed(range(len(bullets))):
                candidates.append((bullets[bullet_idx]["priority"], section, entry_idx, bullet_idx))
    for idx in reversed(range(len(content["achievements"]))):
        candidates.append((content["achievements"][idx]["priority"], "achievements", idx, None))
    return sorted(candidates, key=lambda c: -c[0])
```

### Algorithm
For each font size in `FONT_SIZE_LADDER` (largest → smallest):
- Repeatedly measure `working` content; if it fits → return `(working, font_size, dropped)`.
- If it overflows and the drop queue still has candidates, pop the next-lowest-priority bullet
  from `working` (a deep copy — original content is never mutated), record it in `dropped`,
  and re-measure.
- If the queue is exhausted at this font size, step down to the next smaller font and continue
  (drop_pointer persists, so already-dropped bullets stay dropped across ladder steps).

Hard failure only when **every** font size AND every droppable bullet is exhausted:
```
ERROR: content still exceeds one page at 8.0pt even after dropping N bullets
(M priority-1 bullets remain, cannot drop further). Cut at least 1 more bullet
or shorten a bullet's text, then retry.
```

### Success reporting
Printed **only** when something was actually sacrificed (zero output when content fits at
standard size untouched — matches the seq-diagram skill's theme-fallback warning pattern):
```
WARN: fit at 9.0pt after dropping 3 low-priority bullets:
  - experience[1] bullet: "Optimised API performance via async execution..."
  - projects[3] bullet: "Managed CI-style local build pipeline; structured..."
  - achievements[2] bullet: "Achieved Finalist status at HackLoop and 5th place..."
OK: rendered resume_draft.pdf (1 page, 9.0pt)
```

---

## 8. Full Pipeline

```python
def build_resume(content_path, out_path="resume_draft.pdf"):
    content = json.load(open(content_path))
    validate(content)                       # one-line error, no PDF touched

    page_width, page_height_full = PAGE_SIZE
    content_width = page_width - 2 * MARGIN_SIDE
    usable_height = page_height_full - MARGIN_TOP - MARGIN_BOTTOM - HEADER_HEIGHT_FIXED

    fitted, font_size, dropped = fit_resume(content, usable_height, content_width)

    c = canvas.Canvas(out_path, pagesize=PAGE_SIZE)
    y = draw_header(c, fitted["header"], fitted["has_photo"], page_width)
    y = draw_education_section(c, fitted["education"], font_size, y, content_width)
    y = draw_experience_section(c, fitted["experience"], font_size, y, content_width)
    y = draw_projects_section(c, fitted["projects"], font_size, y, content_width)
    y = draw_skills_section(c, fitted["skills"], font_size, y, content_width)
    draw_achievements_section(c, fitted["achievements"], font_size, y, content_width)
    c.save()

    _report(dropped, font_size, out_path)   # warn-on-sacrifice + OK line
```

Each `draw_*_section` returns the new `y` cursor so the next section continues flush — no
absolute positioning, no page-2 risk because fit already guaranteed one page.

### CLI
`resume-builder content.json [-o out.pdf]` (wired via `[project.scripts]`). Default output is
`resume_draft.pdf` in CWD. Exits non-zero with the one-line error string on validation or
overflow failure; zero with the OK line on success.

---

## 9. Testing Strategy

| Module | Key tests |
|---|---|
| `test_schema.py` | Every validation error message exactly matches the contract string; `priority` absence raises; `has_photo: true` + missing file raises; empty required section raises; out-of-range `priority` raises; valid payload parses. |
| `test_text.py` | `wrap_text` respects `max_width` (stringWidth); long single word overflows gracefully; empty string → `[]`; idempotent on already-wrapped input. |
| `test_measure.py` | `measure_total_height` is monotonic in bullet count; height shrinks when font size decreases; height is deterministic across runs (no mutation of input). |
| `test_fit.py` | Fits at top ladder rung with no drops when content is small; drops priority-3 before priority-2 before priority-1; drop order respects reversed-entry/reversed-bullet tiebreak; drops persist across font steps; hard `OverflowError` when only priority-1 remains and still overflows at 8pt; `dropped` list records truncated text (first 50 chars). |
| `test_pipeline.py` | End-to-end: sample `content.json` → `resume_draft.pdf` exists, is exactly 1 page (via `pypdf` or reportlab page count), no exception. Photo path: monkey-patch `PHOTO_PATH` to a fixture PNG, assert 1-page output and that `make_circular_photo` produced a temp file. |

Use pydantic's `model_validate` + custom `@field_validator`s to emit exact contract strings —
tests assert `str(exc.value).strip() == expected` for determinism.

Fit-engine tests use synthetic content generators (helpers in `tests/conftest.py`) so every
priority/entry-count combination is reachable without hand-authoring huge JSON.

---

## 10. Build Phases / Milestones

1. **M1 — Scaffold & schema:** `pyproject.toml` deps (✅), `resumebuilder/` package skeleton,
   `schema.py` with full validation contract + `test_schema.py` green.
2. **M2 — Text + measure:** `text.py` `wrap_text`, `measure.py` `measure_total_height` +
   `measure_skills_height`, both with passing unit tests.
3. **M3 — Fit engine:** `fit.py` `collect_all_bullets_by_priority` + `fit_resume`, full
   `test_fit.py` covering ladder, drop order, persistence, hard overflow.
4. **M4 — Template + draw:** `template.py` constants, `draw.py` primitives (header, section
   header, entry row, skills, achievements, photo). Visual smoke check against reference PDF.
5. **M5 — Pipeline + CLI:** `pipeline.build_resume`, `cli.main`, `test_pipeline.py`
   end-to-end (assert 1 page, correct output filename).
6. **M6 — Polish:** ruff clean, pytest-cov gate (target ≥90% on `fit`/`measure`/`schema`),
   README snippet, sample `content.json` fixture committed.

---

## 11. Extension Hooks (deferred, not v1)

- **Proper small-caps font** — register an OpenType font with real small-caps glyphs via
  `fonttools` feature lookup; replace `draw_pseudo_small_caps`. Template constant swap only.
- **Two-column skills layout** — fixed deterministic two-column wrap if skills becomes a
  frequent overflow contributor; reclaims vertical space without touching font size.
- **Diff-against-last-run** — keep prior `content.json` alongside the new one and print a
  short diff, useful when iterating on a JD-tailored version across a session.

These are explicitly out of scope for v1 and tracked here only so the architecture leaves room:
`template.py` is the single seam — swapping constants or `draw_*` functions there does not
touch `fit` / `measure` / `schema`.

---

## 12. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Measurement drift vs. real render (leading/spacing mismatch) → overflow unnoticed. | Derive all heights from the same locked constants in `template.py`; round-trip test asserts rendered page count == 1 on the sample fixture. |
| `stringWidth` differs from Break-Opportunity logic (long URLs). | `wrap_text` is greedy on whitespace; acceptable for resume prose. Document that long unbreakable tokens may overflow a line — not a page-level risk. |
| Pydantic error strings drifting from the contract. | Tests assert exact `str(exc.value)` for every contract case; ruff CI block merges that change strings without updating tests. |
| Photo missing at render time after `has_photo: true`. | Validation checks file existence **before** `Canvas` is created — fails fast, no temp files left behind. |
| Agent mutates `content.json` in place expecting drop-side-effects. | `fit_resume` operates on a `copy.deepcopy` — original content is never mutated. |

---