"""Pydantic models for the resume YAML schema — cv + design + settings."""
import os

import pydantic


class BaseModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")


# ── Design ──────────────────────────────────────────────────────────

class PageModel(BaseModel):
    size: str = "us-letter"
    top_margin: str = "0.5in"
    bottom_margin: str = "0.5in"
    left_margin: str = "0.6in"
    right_margin: str = "0.6in"


class Typography(BaseModel):
    body_font: str = "Times New Roman"
    body_size: str = "1.5pt"
    name_font: str = "Times New Roman"
    name_size: str = "0.1pt"
    name_bold: bool = True
    headline_font: str = "Times New Roman"
    headline_size: str = "1.5pt"
    connections_font: str = "Times New Roman"
    connections_size: str = "0.9pt"
    section_title_font: str = "Times New Roman"
    section_title_size: str = "1.5pt"
    section_title_bold: bool = True
    section_title_tracking: str = "0.8pt"
    line_spacing: str = "0.3em"
    justify_body: bool = True


class HeaderDesign(BaseModel):
    connections_separator: str = "  •  "
    connections_spacing: str = "0.5cm"
    connections_color: str = "555"
    space_below_name: str = "0cm"
    space_below_headline: str = "0.10cm"
    space_below_connections: str = "0.40cm"


class SectionTitles(BaseModel):
    type: str = "with-full-line"
    line_thickness: str = "0.6pt"
    space_above: str = "0.12cm"
    space_below: str = "0.12cm"


class EntriesDesign(BaseModel):
    date_column_width: str = "4.15cm"
    column_gap: str = "0.1cm"
    space_between_entries: str = "0.2cm"
    bullet_char: str = "•"
    bullet_indent: str = "0.35cm"
    bullet_text_gap: str = "0.5em"
    degree_column_width: str = "1cm"
    summary_space_above: str = "0.1cm"


class Design(BaseModel):
    page: PageModel = pydantic.Field(default_factory=PageModel)
    typography: Typography = pydantic.Field(default_factory=Typography)
    header: HeaderDesign = pydantic.Field(default_factory=HeaderDesign)
    section_titles: SectionTitles = pydantic.Field(default_factory=SectionTitles)
    entries: EntriesDesign = pydantic.Field(default_factory=EntriesDesign)


# ── CV ──────────────────────────────────────────────────────────────

class SocialNetwork(BaseModel):
    network: str
    username: str


class Cv(BaseModel):
    name: str
    headline: str | None = None
    location: str | None = None
    email: str | None = None
    phone: str | None = None
    social_networks: list[SocialNetwork] | None = None
    photo: str | None = None


class EducationEntry(BaseModel):
    institution: str
    location: str | None = None
    area: str
    degree: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    date: str | None = None
    highlights: list[str] | None = None


class ExperienceEntry(BaseModel):
    company: str
    position: str
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    date: str | None = None
    summary: str | None = None
    highlights: list[str] | None = None


class NormalEntry(BaseModel):
    name: str
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    date: str | None = None
    summary: str | None = None
    highlights: list[str] | None = None


class OneLineEntry(BaseModel):
    label: str
    details: str


class BulletEntry(BaseModel):
    bullet: str


# ── Top-level ───────────────────────────────────────────────────────

class Settings(BaseModel):
    output_filename: str = "resume_draft.pdf"


class ResumeContent(BaseModel):
    cv: Cv
    education: list[EducationEntry] = pydantic.Field(default_factory=list, min_length=1)
    experience: list[ExperienceEntry] = pydantic.Field(default_factory=list)
    projects: list[NormalEntry] = pydantic.Field(default_factory=list)
    skills: list[OneLineEntry] = pydantic.Field(default_factory=list, min_length=1)
    achievements: list[BulletEntry] = pydantic.Field(default_factory=list)
    design: Design = pydantic.Field(default_factory=Design)
    settings: Settings = pydantic.Field(default_factory=Settings)

    @pydantic.model_validator(mode="after")
    def check_photo_exists(self):
        if self.cv.photo and not os.path.isfile(os.path.expanduser(self.cv.photo)):
            raise ValueError(f"Photo file not found: {self.cv.photo}")
        return self


Validate = pydantic.TypeAdapter(ResumeContent)
