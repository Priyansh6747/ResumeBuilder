{% if design.section_titles.space_above %}#v({{ design.section_titles.space_above }}){% endif %}
#text(size: {{ design.typography.section_title_size }}, weight: "bold")[{{ section_title | upper }}]
#v(0.10cm)
#line(stroke: {{ design.section_titles.line_thickness }}, length: 100%)
{% if design.section_titles.space_below %}#v({{ design.section_titles.space_below }}){% endif %}
