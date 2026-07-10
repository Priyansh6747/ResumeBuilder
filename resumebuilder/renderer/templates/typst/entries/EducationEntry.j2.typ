#text(weight: "bold")[{{ entry.institution }}]  #text(size: 10pt)[{{ entry.date }}]


#text(size: 9.5pt)[{{ entry.area }}{% if entry.degree %}  |  Degree: {{ entry.degree }}{% endif %}]


{% if entry.highlights %}
{% for h in entry.highlights %}
#v(0.05cm)
#text(size: 9.5pt)[  {{ design.entries.bullet_char }}  {{ h }}]
{% endfor %}


{% endif %}
{% if design.entries.space_between_entries %}#v({{ design.entries.space_between_entries }}){% endif %}
