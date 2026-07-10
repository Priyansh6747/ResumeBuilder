#align(center)[
  #text(size: {{ design.typography.name_size }}, weight: "bold", tracking: 0.02em)[{{ cv.name | upper }}]
{% if cv._connections %}
  #v(1pt)
  #text(size: {{ design.typography.connections_size }}, fill: rgb("{{ design.header.connections_color }}"))[{{ cv._connections | join("  •  ") }}]
{% endif %}
{% if cv.headline %}
  #v(1pt)
  #text(size: {{ design.typography.headline_size }}, style: "italic")[{{ cv.headline }}]
{% endif %}
]

#v({{ design.header.space_below_connections }})
