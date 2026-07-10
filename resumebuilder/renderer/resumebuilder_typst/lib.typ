// resumebuilder_typst/lib.typ — Self-contained resume layout helpers
// Design config flows in via #show: resumebuilder.with(...)

#let resumebuilder-config = state("resumebuilder-config", (:))

// ── Header ──────────────────────────────────────────────────────────

#let name(body) = {
  context {
    let c = resumebuilder-config.get()
    set text(
      font: c.at("name-font", "Times New Roman"),
      size: c.at("name-size", 22pt),
      weight: if c.at("name-bold", true) { "bold" } else { "regular" },
    )
    body
    v(c.at("space-below-name", 0.3cm), weak: true)
  }
}

#let headline(body) = {
  context {
    let c = resumebuilder-config.get()
    set text(
      font: c.at("headline-font", "Times New Roman"),
      size: c.at("headline-size", 9.5pt),
    )
    body
    v(c.at("space-below-headline", 0.15cm), weak: true)
  }
}

#let connections(..items) = {
  context {
    let c = resumebuilder-config.get()
    let sep = c.at("connections-separator", "  |  ")
    let spacing = c.at("connections-spacing", 0.5cm)
    set text(
      font: c.at("connections-font", "Times New Roman"),
      size: c.at("connections-size", 9.5pt),
    )
    let parts = items.pos()
    if parts.len() > 0 {
      let rendered = parts.first()
      for item in parts.slice(1) {
        rendered = [#rendered#sep#item]
      }
      rendered
      v(c.at("space-below-connections", 0.35cm), weak: true)
    }
  }
}

// ── Section titles ───────────────────────────────────────────────────

#let section-title(title) = {
  context {
    let c = resumebuilder-config.get()
    let style = c.at("section-title-type", "with-full-line")
    let rule-thickness = c.at("section-title-rule-thickness", 0.6pt)
    let space-above = c.at("space-above-section-title", 0.3cm)
    let space-below = c.at("space-below-section-title", 0.1cm)

    v(space-above, weak: true)
    set text(
      font: c.at("section-title-font", "Times New Roman"),
      size: c.at("section-title-size", 10.5pt),
      weight: if c.at("section-title-bold", true) { "bold" } else { "regular" },
      tracking: c.at("section-title-tracking", 0.8pt),
    )

    if style == "with-full-line" {
      upper(title)
      v(0.06cm)
      line(stroke: rule-thickness, length: 100%)
    } else if style == "without-line" {
      upper(title)
    } else {
      upper(title)
      v(0.06cm)
      line(stroke: rule-thickness, length: 100%)
    }

    v(space-below, weak: true)
  }
}

// ── Entries ──────────────────────────────────────────────────────────

#let regular-entry(main-column, date-column, second-row: none) = {
  context {
    let c = resumebuilder-config.get()
    let date-width = c.at("date-column-width", 4.15cm)
    let col-gap = c.at("entries-column-gap", 0.1cm)
    let entry-gap = c.at("space-between-entries", 0.2cm)
    let justify = c.at("justify-body", true)

    set par(justify: justify)

    grid(
      columns: (1fr, date-width),
      column-gutter: col-gap,
      align: (left, right),
      [#main-column],
      [#date-column],
    )

    if second-row != none {
      set align(left)
      second-row
    }

    v(entry-gap, weak: true)
  }
}

#let education-entry(main-column, date-column, degree-column: none, second-row: none) = {
  context {
    let c = resumebuilder-config.get()
    let degree-width = c.at("degree-column-width", 1cm)
    let date-width = c.at("date-column-width", 4.15cm)
    let col-gap = c.at("entries-column-gap", 0.1cm)
    let entry-gap = c.at("space-between-entries", 0.2cm)

    if degree-column != none {
      grid(
        columns: (degree-width, 1fr, date-width),
        column-gutter: col-gap,
        align: (left, left, right),
        [#degree-column],
        [#main-column],
        [#date-column],
      )
    } else {
      grid(
        columns: (1fr, date-width),
        column-gutter: col-gap,
        align: (left, right),
        [#main-column],
        [#date-column],
      )
    }

    if second-row != none {
      set align(left)
      second-row
    }

    v(entry-gap, weak: true)
  }
}

#let one-line-entry(content) = {
  context {
    let c = resumebuilder-config.get()
    let entry-gap = c.at("space-between-entries", 0.2cm)
    content
    v(entry-gap, weak: true)
  }
}

#let bullet-entry(content) = {
  context {
    let c = resumebuilder-config.get()
    let bullet = c.at("bullet-char", "•")
    let bullet-indent = c.at("bullet-indent", 0.35cm)
    let bullet-gap = c.at("bullet-text-gap", 0.5em)
    let entry-gap = c.at("space-between-entries", 0.2cm)
    par(
      first-line-indent: bullet-indent,
      hanging-indent: bullet-indent,
    )[#bullet #content]
    v(entry-gap, weak: true)
  }
}

#let summary(content) = {
  context {
    let c = resumebuilder-config.get()
    let summary-gap = c.at("summary-space-above", 0.1cm)
    set par(justify: true)
    v(summary-gap, weak: true)
    content
  }
}

#let highlight(content) = {
  context {
    let c = resumebuilder-config.get()
    let bullet = c.at("bullet-char", "•")
    let bullet-indent = c.at("bullet-indent", 0.35cm)
    let bullet-gap = c.at("bullet-text-gap", 0.5em)
    let line-spacing = c.at("line-spacing", 0.6em)
    par(
      first-line-indent: bullet-indent,
      hanging-indent: bullet-indent,
      leading: line-spacing,
    )[#bullet #content]
  }
}

// ── Show rule ────────────────────────────────────────────────────────

#let resumebuilder(body, ..config) = {
  let c = config.named()

  set page(
    paper: c.at("page-size", default: "us-letter"),
    margin: (
      top: c.at("page-top-margin", default: 0.5in),
      bottom: c.at("page-bottom-margin", default: 0.5in),
      left: c.at("page-left-margin", default: 0.6in),
      right: c.at("page-right-margin", default: 0.6in),
    ),
  )

  set text(
    font: c.at("body-font", default: "Times New Roman"),
    size: c.at("body-size", default: 9.5pt),
  )

  set par(leading: c.at("line-spacing", default: 0.6em))

  resumebuilder-config.update(c)
  body
}
