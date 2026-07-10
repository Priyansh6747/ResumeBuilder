// Typst set-up — compact, body left-aligned
#set page(paper: "{{ design.page.size }}", margin: (
  top: {{ design.page.top_margin }},
  bottom: {{ design.page.bottom_margin }},
  left: {{ design.page.left_margin }},
  right: {{ design.page.right_margin }},
))
#set text(font: "{{ design.typography.body_font }}", size: {{ design.typography.body_size }})
#set par(leading: {{ design.typography.line_spacing }}, justify: {{ design.typography.justify_body | lower }})
