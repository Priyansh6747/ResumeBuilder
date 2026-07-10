# ResumeBuilder

Typst-based one-page resume PDF renderer — YAML in, pixel-perfect PDF out.

## Install

```bash
uv sync
```

## Use

```bash
uv run python -m resumebuilder sample_content.yaml
# → resume_draft.pdf
```

Custom output path:

```bash
uv run python -m resumebuilder sample_content.yaml -o my_resume.pdf
```

## YAML format

Three top-level blocks: `cv` (header), section lists, and `design` (layout config).

### `cv` — header

```yaml
cv:
  name: Your Name
  headline: Role or tagline
  email: you@example.com
  phone: "+1-555-1234"
  social_networks:
    - network: LinkedIn
      username: yourname
    - network: GitHub
      username: yourgithub
```

### Sections

```yaml
education:
  - institution: University
    area: Computer Science
    degree: B.Tech
    start_date: "2023"
    end_date: "2027"
    highlights:
      - "Coursework: Data Structures, Algorithms, OS"

experience:
  - company: Acme Corp
    position: Software Engineer
    start_date: Jan 2024
    end_date: present
    summary: Built the main product
    highlights:
      - "Led migration of monolithic API to microservices"
      - "Mentored 3 junior engineers"

projects:
  - name: My Project
    start_date: 2025
    end_date: 2025
    summary: A short description
    highlights:
      - "Built a thing that does stuff"

skills:
  - label: Languages
    details: Python, Rust, TypeScript
  - label: Tools
    details: Docker, Kubernetes, Terraform

achievements:
  - bullet: "Top 3 Nationally — Hackathon 2025"
  - bullet: "Published open-source library on crates.io"
```

### `design` — layout (optional, defaults shown)

```yaml
design:
  page:
    size: us-letter
    top_margin: 0.5in
    bottom_margin: 0.5in
    left_margin: 0.6in
    right_margin: 0.6in
  typography:
    body_font: Times New Roman
    body_size: 9.5pt
    name_size: 22pt
    headline_size: 9.5pt
    connections_size: 9.5pt
    section_title_size: 10.5pt
    section_title_bold: true
    line_spacing: 0.6em
    justify_body: true
  header:
    connections_separator: "  |  "
    space_below_name: 0.3cm
    space_below_headline: 0.15cm
    space_below_connections: 0.35cm
  section_titles:
    type: with-full-line
    line_thickness: 0.6pt
    space_above: 0.3cm
    space_below: 0.1cm
  entries:
    bullet_char: "•"
    bullet_indent: 0.35cm
    date_column_width: 4.15cm
    space_between_entries: 0.2cm
    degree_column_width: 1cm
```

## Architecture

```
sample_content.yaml
      ↓  ruamel.yaml parse
      ↓  pydantic validation
      ↓  Jinja2 templates → Typst markup
      ↓  typst-py compiler → PDF
resume_draft.pdf
```

Typst handles all layout — text wrapping, line spacing, page fitting. No manual
measurement or cursor tracking.

## Dependencies

- `typst` — PDF compilation
- `Jinja2` — template rendering
- `pydantic` — schema validation
- `ruamel.yaml` — YAML parsing with line-info preservation
