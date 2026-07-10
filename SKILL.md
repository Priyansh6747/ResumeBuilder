# ResumeBuilder Skill

You are building a resume as a YAML file that gets rendered to a one-page PDF
via Typst. The resume builder owns 100% of visual formatting — you own 100%
of content.

## The only file you write

`content.yaml` — three sections:

1. **`cv`** — header: name, headline, email, phone, social_networks
2. **Section lists** — education, experience, projects, skills, achievements
3. **`design`** (optional) — layout overrides; leave it out to accept defaults

## Entry types

| Section | Entry fields |
|---|---|
| `education` | `institution` (required), `area`, `degree`, `start_date`, `end_date`, `highlights[]` |
| `experience` | `company`, `position` (required), `start_date`, `end_date`, `summary`, `highlights[]` |
| `projects` | `name` (required), `start_date`, `end_date`, `summary`, `highlights[]` |
| `skills` | `label`, `details` (required) — renders as `**Label:** details` |
| `achievements` | `bullet` (required) — renders as `• bullet` |

## Date formats

Any of these work — they're passed through as-is:

```yaml
start_date: "2023"
end_date: 2027
start_date: "Nov 2025"
end_date: present
start_date: "2025-05"
end_date: "2025-10"
```

## Layout rules you must follow

1. **Content fits one page** — Typst handles page-fit, but you control
   how much content goes in. If it overflows, cut bullet points before
   adding a second page.
2. **Order matters** — experience and project entries render in YAML array
   order. Put strongest entries first.
3. **No visual formatting** — you write ONLY text. The skill owns margins,
   fonts, colors, spacing, and section title style. Never include
   `font_size`, `color`, `margin`, or any layout value in your YAML.
4. **Bold/italic** — use plain text. Markdown markup (`**bold**`) is not
   converted to Typst and will render literally.

## Validation errors

The builder fails fast with one-line errors before touching any PDF:

- `education` and `skills` sections must have at least one entry
- `cv.name` is required
- A `photo` field pointing to a missing file raises an error

## Running

```bash
uv run python -m resumebuilder content.yaml
# → resume_draft.pdf
```

## Design block (you don't write this)

The `design:` block controls all layout. The defaults are a clean classic
template (Times New Roman, 9.5pt body, 22pt name, section titles with full-width
hairline rules). If you need a different look, the design block supports:

- Page size and margins
- Font family and size per element (body, name, headline, connections, section titles)
- Section title style, rule thickness, spacing
- Bullet character, indentation, and entry spacing
- Connections separator (default `  |  `) and spacing
