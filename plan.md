# Resume Builder — Implementation Plan (Typst Pipeline)

> **Status}: Working pipeline produces PDFs. Category 7 (cleanup) and
> Category 6 (tests) remain. Optional Jinja2 template wiring is deferred
> until the string-concat renderer proves insufficient.

---

## 0. Current Implementation Status (audit date: 2025-07-10)

A thorough audit was performed against the earlier plan. Here is the
real state, phase by phase.

### Working pipeline (active code path)

```
sample_content.yaml
      ↓
cli.py (resume-builder content.yaml -o out.pdf)
      ↓
pipeline.build_resume()
      ↓
schema/__init__.py::read_yaml()     ← ruamel.yaml, preserves line info
      ↓
schema/models.py::Validate          ← pydantic TypeAdapter(ResumeContent)
      ↓
renderer/typst_renderer.py          ← hand-built Typst via string concat
      ↓
renderer/compiler.py                ← typst-py → PDF
      ↓
resume_draft.pdf
```

**This pipeline runs and produces single-page PDFs.** It uses raw Typst
directives (`#set page`, `#text`, `#v`, `#line`) rather than the
rendercv Typst package (`#import "@preview/rendercv:0.3.0"`), which
means it does NOT depend on bundling `rendercv_typst/` or
`typst_fontawesome/` — a simpler approach than the earlier plan
described.

### Phase tracker

| # | Phase | Status | Notes |
|---|---|---|---|
| 1 | pyproject.toml + deps | DONE | `typst`, `rendercv-fonts`, `Jinja2`, `pydantic[email]`, `ruamel.yaml` installed. `reportlab`/`Pillow` removed. **Jinja2 and rendercv-fonts currently unused** — declared ahead of need. |
| 2 | Schema models | PARTIAL | `schema/models.py` is a flat file with `ResumeContent` (top-level sections, no `design`/`settings` blocks). No `Section` auto-type-detection, no `Design`/`ClassicTheme`/`Color`/`FontFamily` models. Entry types are explicit fields, not auto-detected by characteristic fields. |
| 3 | Templater (Jinja2) | STUB | 9 `.j2.typ` template files exist in `renderer/templates/typst/` but **nothing renders them**. `typst_renderer.py` builds Typst via Python string concatenation and ignores the templates entirely. Dead assets. |
| 4 | Renderer | PARTIAL | `compiler.py` (typst-py wrapper) + `typst_renderer.py` (string-concat generator) work. **Missing**: `path_resolver.py`, `pdf_png.py`, bundled `rendercv_typst/`, `typst_fontawesome/`. Not needed if we keep raw-Typst-directive approach. |
| 5 | CLI + pipeline wiring | DONE | `cli.py` accepts `.yaml`, calls `build_resume()`. `pipeline.py` rewired to new pipeline. `__init__.py` exports `build_resume` from `pipeline`. |
| 6 | Tests | MISSING | All 5 test files still import the old reportlab modules (`from resumebuilder.schema import validate`, `from resumebuilder.fit import ...`, `from resumebuilder.text import wrap_text`). **All 5 error on collection** because `reportlab` is no longer installed and `schema.py` is shadowed by the `schema/` package. No e2e YAML→PDF test exists. |
| 7 | Cleanup | NOT STARTED | `formatting_engine/` (10 files), `draw.py`, `measure.py`, `fit.py`, `template.py` (old), `text.py`, `schema.py` (old, shadowed by package) — all still present. `sample_content.json` still present. `clean.typ`, `resume.typ` (debug artifacts) present. |

### Key divergences from the earlier plan

1. **No `design:` / `settings:` blocks in the YAML.** The
   `sample_content.yaml` puts sections at the top level (not under
   `cv.sections.`), and there is no `design:` hierarchy. Design
   parameters (margins, fonts, sizes) are hardcoded in
   `typst_renderer.py`.
2. **No Jinja2 templating.** `typst_renderer.py` writes Typst source
   via `lines.append(f'#text(...)')` — the `.j2.typ` files are
   unused. This works but makes layout changes require editing Python
   string templates.
3. **No rendercv Typst package.** The renderer uses raw
   `#set page(...)` / `#text(...)` directives, not the
   `#import "@preview/rendercv:0.3.0"` system. This means no bundled
   package directory is needed.
4. **`schema.py` vs `schema/` package collision.** Both exist. Python
   resolves `import resumebuilder.schema` to the **package** (directory),
   so `schema.py` is dead. But the old `formatting_engine/engine.py`
   still imports `from resumebuilder.schema import validate` — which
   now fails (the package has no `validate` export).
5. **`_sanitize()` regex hack in `typst_renderer.py`.** Strips
   `X_Y`→`XY` to dodge a Typst 0.15 lexer issue with underscores. This
   is a fragile workaround that may corrupt content.

---

## 1. Why the reportlab approach was abandoned

| Problem | Root cause |
|---|---|
| Stray rule lines cutting through text | y-cursor drift between `measure()` and `draw()` |
| Over-trimming despite blank space on page | `measure_total_height` overestimated real rendered height |
| HEADER_HEIGHT_FIXED didn't include contact line | Manual height bookkeeping can't match automatic layout |
| Font-size fallback ladder needed | Reportlab has no automatic page-fit; we had to simulate it |
| Every spacing change required updating 3+ files | template.py, measure.py, draw.py, HEADER_HEIGHT_FIXED all had to stay in lockstep |

**Typst eliminates all of these}: the typesetting engine handles
wrapping, spacing, and page-fit. We just generate markup; Typst handles
layout.

---

## 2. The Active Pipeline

```
sample_content.yaml          ← Agent writes: content (no layout)
        ↓
ruamel.yaml parse           ← Preserves comments/line info for error messages
        ↓
pydantic validation          ← Type-check content, produce one-line errors
        ↓
typst_renderer.py → .typ     ← Python string concat → Typst markup
        ↓
typst-py compiler → .pdf     ← Typst handles ALL layout (wrapping, spacing, page-fit)
        ↓
resume_draft.pdf
```

### Why each stage

| Stage | Lib | Why |
|---|---|---|
| YAML parse | `ruamel.yaml` | Preserves source positions → user-friendly error messages |
| Validation | `pydantic>=2.12` | Type coercion, custom validators for one-line errors |
| Typst generation | `typst_renderer.py` (string concat) | Sections rendered one-by-one, stitched into a single .typ string |
| PDF compile | `typst>=0.14.8` | Typst handles wrapping, spacing, columns, page-fit — no manual measurement |

---

## 3. Dependencies (pyproject.toml)

```toml
dependencies = [
    "typst>=0.14.8",           # Typst Python bindings → PDF compilation
    "rendercv-fonts>=0.5.1",   # Bundled fonts (declared, not yet wired)
    "Jinja2>=3.1.6",           # Template engine (declared, not yet wired)
    "pydantic[email]>=2.12.5", # Content schema validation
    "ruamel.yaml>=0.19.1",     # YAML parsing with line-info preservation
]
```

**Jinja2 and rendercv-fonts** are declared ahead of need. They become
active if Phase 3 (Jinja2 template wiring) or a font-resolution path
is implemented. Currently unused.

---

## 4. YAML Content Format

The YAML has one top-level key: `cv` (header info) plus top-level
section lists. No `design:` or `settings:` blocks yet — design
parameters are hardcoded in `typst_renderer.py`.

```yaml
cv:
  name: Priyansh Singh
  headline: DevOps & Full Stack Engineer Intern | B.Tech CSE 2027
  email: pstanwar6747@gmail.com
  phone: "+91-8107173094"
  social_networks:
    - network: LinkedIn
      username: priyanshsingh6747
    - network: GitHub
      username: Priyansh6747

education:
  - institution: Jaypee Institute of Information Technology (JIIT)
    area: Computer Science and Engineering
    degree: B.Tech
    start_date: "2023"
    end_date: "2027"

experience:
  - company: US-Based Startup (Remote)
    position: Freelance Full-Stack Developer
    start_date: Nov 2025
    end_date: present
    highlights:
      - "Engineered microservices backend..."

projects:
  - name: CareNest
    summary: Maternal & child healthcare platform
    start_date: May 2025
    end_date: Oct 2025
    highlights:
      - "Built full-stack RAG system..."

skills:
  - label: Languages
    details: Rust, C++, Python, JavaScript, TypeScript, SQL

achievements:
  - bullet: "Top 3 Nationally — AI x MedTech Startup Hackathon 2025"
```

### Entry types (field-validated)

| Entry type | Characteristic fields | Used for |
|---|---|---|
| `EducationEntry` | `institution`, `area` | Education section |
| `ExperienceEntry` | `company`, `position` | Experience section |
| `NormalEntry` | `name` | Projects section |
| `OneLineEntry` | `label`, `details` | Skills section |
| `BulletEntry` | `bullet` | Achievements section |

Types are **not auto-detected** (unlike rendercv) — they're explicit
fields on the `ResumeContent` model
(`education: list[EducationEntry]`, etc.). Simpler, less magic.

### Why `priority` is gone

The old JSON had `bullets[].priority` (1-3) for the fit/trim engine.
Typst handles page-fit automatically, so priority-based trimming is
unnecessary. The agent controls fit by choosing what to include. If
priority-based trimming is ever needed, it can be a pre-processing
step before Typst generation — not part of the rendering pipeline.

---

## 5. Actual Module Layout

```
resumebuilder/
├── __init__.py               # exports build_resume from pipeline
├── __main__.py               # python -m resumebuilder
├── cli.py                    # resume-builder content.yaml [-o out.pdf]  ✅
├── pipeline.py               # read_yaml → Validate → generate_typst → compile  ✅
├── schema/                   # NEW (YAML + pydantic)
│   ├── __init__.py           # read_yaml(), ReadError, ScannerNoAlias  ✅
│   └── models.py             # ResumeContent, entry models, Validate  ✅ (no design models)
├── renderer/                 # NEW (Typst)
│   ├── typst_renderer.py     # generate_typst() — string concat  ✅
│   ├── compiler.py           # compile_typst() — typst-py wrapper  ✅
│   └── templates/typst/      # .j2.typ files  ⚠️ UNUSED (dead assets)
│       ├── Preamble.j2.typ
│       ├── Header.j2.typ
│       ├── SectionBeginning.j2.typ
│       ├── SectionEnding.j2.typ
│       └── entries/*.j2.typ
├── schema.py                 # LEGACY (shadowed by schema/ package, dead)
├── draw.py                   # LEGACY (imports reportlab, dead)
├── measure.py               # LEGACY (delegates to formatting_engine, dead)
├── fit.py                    # LEGACY (delegates to formatting_engine, dead)
├── template.py               # LEGACY (imports reportlab, dead)
├── text.py                   # LEGACY (imports reportlab, dead)
└── formatting_engine/        # LEGACY (entire reportlab pipeline, dead)
    ├── engine.py
    ├── fit.py
    ├── template.py
    ├── text.py
    ├── photo.py
    └── blocks/*.py
```

---

## 6. What Eliminating Reportlab Eliminated

| Old concern | Eliminated because |
|---|---|
| `measure_total_height()` | Typst measures and lays out automatically |
| `fit_resume()` / font ladder | Typst handles page-fit |
| `BULLET_SPACING_AFTER` etc. | Hardcoded in `typst_renderer.py` as `#v(0.15cm)` |
| `HEADER_HEIGHT_FIXED` | Typst calculates header height from content |
| `wrap_text()` | Typst wraps text automatically |
| `make_circular_photo()` | Typst template directive for photo masking |
| `draw_section_header()` | Typst `#text(...) + #line(...)` in `typst_renderer.py` |
| `_leading()`, `stringWidth()` | Typst handles line height, font metrics |
| Measurement/draw drift | No manual measurement at all — **impossible to drift** |
| Stray rule lines | Typst renders section headers as a unit; no y-cursor bugs |
| Over-trimming | No trim engine needed |

---

## 7. Remaining Work

### 7a. Cleanup (delete legacy code) — HIGH PRIORITY

Delete these files/directories — they are dead, cause import collisions,
and will confuse any future reader:

```
resumebuilder/formatting_engine/     (entire directory, 10+ files)
resumebuilder/draw.py
resumebuilder/measure.py
resumebuilder/fit.py
resumebuilder/template.py            (old reportlab template)
resumebuilder/text.py                (old reportlab text wrapper)
resumebuilder/schema.py              (old, shadowed by schema/ package)
sample_content.json                  (replaced by sample_content.yaml)
clean.typ                            (debug artifact)
resume.typ                           (debug artifact)
```

After deletion, `resumebuilder.schema` resolves cleanly to the package.
`from resumebuilder.schema import read_yaml, ReadError` — currently
works, but the shadowed `schema.py` makes it fragile.

### 7b. Tests — HIGH PRIORITY

All 5 test files are broken. They import from the old reportlab
modules. They need to be rewritten or deleted:

| Old test | Action |
|---|---|
| `test_schema.py` | Rewrite: test `ResumeContent` pydantic model, `Validate.validate_python()`, field validation, error messages |
| `test_pipeline.py` | Rewrite: end-to-end `sample_content.yaml → resume_draft.pdf`, assert PDF exists, is 1 page |
| `test_fit.py` | Delete (fit engine gone, replaced) |
| `test_measure.py` | Delete (measure engine gone, replaced) |
| `test_text.py` | Delete (wrap_text gone, replaced by Typst) |
| `conftest.py` | Rewrite: YAML content builders instead of old JSON builders |

New tests to add:
- `test_renderer.py` — `generate_typst(data)` produces valid Typst source
  (contains expected section headers, entries, bullets)
- `test_compiler.py` — `compile_typst(source, output)` produces a PDF
  file that exists and is non-empty
- End-to-end: `sample_content.yaml → resume_draft.pdf` produces a
  1-page PDF

### 7c. Schema: optionally add `design` block — MEDIUM PRIORITY

Currently design parameters (margins, fonts, sizes, spacing) are
hardcoded in `typst_renderer.py`. If a `design:` block were added to
both the YAML and the pydantic model, these could be configurable
without code changes:

```yaml
design:
  page:
    size: us-letter
    margin: { top: 0.5in, bottom: 0.5in, left: 0.6in, right: 0.6in }
  typography:
    font: "Times New Roman"
    body_size: 9.5pt
    name_size: 22pt
  section_titles:
    rule: true
    space_above: 0.30cm
    space_below: 0.06cm
```

This is a **medium-priority** enhancement. The hardcoded approach
works fine for a fixed personal template, which is the current use
case.

### 7d. Optionally wire Jinja2 templates — LOW PRIORITY

The 9 `.j2.typ` files in `renderer/templates/typst/` exist but are
unused. They could replace the string-concatenation in
`typst_renderer.py` with a Jinja2-driven approach
(copied from rendercv's `templater.py`). Benefits:
- Layout changes edit templates, not Python strings
- Multi-format support (add .j2.md for Markdown output)
- User-overridable templates

Currently the string-concat renderer works and is simpler. Defer Jinja2
wiring until the string-concat approach proves insufficient.

### 7e. Remove `_sanitize()` hack — MEDIUM PRIORITY

`typst_renderer.py` has a `_sanitize()` function that strips
underscores from content via regex (`re.sub(r'([^a-zA-Z])_([a-zA-Z])', ...)`
to dodge a Typst 0.15 lexer bug. This can corrupt legitimate content
(e.g., `gemini_light_rs` → `geminilightrs`). Fix: escape underscores in
Typst markup properly or upgrade typst-py to a version with the fix.

### 7f. Add `renderer/__init__.py` — LOW PRIORITY

`renderer/` is currently a namespace package (no `__init__.py`). It
should have one to make it a proper package and enable clean imports.

---

## 8. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| `_sanitize()` corrupts content with underscores | Escape underscores in Typst markup instead of stripping them |
| `schema.py` / `schema/` collision causes confusion | Delete `schema.py` (Phase 7a cleanup) |
| Jinja2 + rendercv-fonts declared but unused | Acceptable — declared ahead of need, or remove if unused long-term |
| No `design:` block means layout requires code changes | Acceptable for fixed template; add `design:` block if external configurability is needed |
| Tests broken | Rewrite tests (Section 7b) |
| Markdown bold/italic in YAML fields not converted to Typst | Fields rendered as raw Typst — `**bold**` won't render as bold in Typst. Add markdown→Typst converter if needed. |

---

## 9. Migration Path (old JSON → new YAML)

```
header.name           → cv.name
header.tagline        → cv.headline
header.phone          → cv.phone
header.email          → cv.email
header.linkedin       → cv.social_networks[0] (network: LinkedIn, username: ...)
header.github         → cv.social_networks[1] (network: GitHub, username: ...)

education[].institution → education[].institution
education[].degree       → education[].area (without "B.Tech in")
                          + education[].degree = "B.Tech"
education[].location     → education[].location
education[].dates        → education[].start_date + end_date

experience[].title       → experience[].position
experience[].org         → experience[].company
experience[].dates       → experience[].start_date + end_date
experience[].bullets[]   → experience[].highlights[] (drop priority)

projects[].name          → projects[].name
projects[].stack         → projects[].summary
projects[].dates         → projects[].start_date + end_date
projects[].bullets[]     → projects[].highlights[] (drop priority)

skills[].category        → skills[].label
skills[].items           → skills[].details

achievements[].text      → achievements[].bullet
achievements[].priority  → (dropped)
```