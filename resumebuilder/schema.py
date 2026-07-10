import os

from pydantic import BaseModel, Field, field_validator, model_validator


class Bullet(BaseModel):
    text: str
    priority: int


class EducationEntry(BaseModel):
    institution: str
    location: str
    degree: str
    dates: str


class ExperienceEntry(BaseModel):
    title: str
    org: str
    dates: str
    bullets: list[Bullet] = Field(default_factory=list)


class ProjectEntry(BaseModel):
    name: str
    stack: str
    dates: str
    bullets: list[Bullet] = Field(default_factory=list)


class SkillGroup(BaseModel):
    category: str
    items: str


class Achievement(BaseModel):
    text: str
    priority: int


class Header(BaseModel):
    name: str
    phone: str
    email: str
    linkedin: str
    github: str
    tagline: str


class ResumeContent(BaseModel):
    has_photo: bool = False
    header: Header
    education: list[EducationEntry]
    experience: list[ExperienceEntry] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)
    skills: list[SkillGroup]
    achievements: list[Achievement] = Field(default_factory=list)

    @field_validator("education")
    @classmethod
    def education_not_empty(cls, v):
        if len(v) == 0:
            raise ValueError('ERROR: "education" section is empty — at least one entry required')
        return v

    @field_validator("skills")
    @classmethod
    def skills_not_empty(cls, v):
        if len(v) == 0:
            raise ValueError('ERROR: "skills" section is empty — at least one entry required')
        return v

    @model_validator(mode="after")
    def check_photo_exists(self):
        if self.has_photo:
            expanded = os.path.expanduser("~/resume_photo.jpg")
            if not os.path.isfile(expanded):
                raise ValueError(
                    "ERROR: has_photo is true but no file found at ~/resume_photo.jpg"
                )
        return self


def _check_bullet_priorities(section_name, entries, bullet_key="bullets"):
    for entry_idx, entry in enumerate(entries):
        bullets = entry.get(bullet_key, [])
        for bullet_idx, bullet in enumerate(bullets):
            priority = bullet.get("priority")
            if priority is None:
                raise ValueError(
                    f'ERROR: {section_name}[{entry_idx}].{bullet_key}[{bullet_idx}] '
                    f'missing required field "priority"'
                )
            if not isinstance(priority, int) or priority not in (1, 2, 3):
                raise ValueError(
                    f"ERROR: {section_name}[{entry_idx}].{bullet_key}[{bullet_idx}]."
                    f"priority must be 1, 2, or 3 (got {priority})"
                )


def _check_achievement_priorities(entries):
    for idx, entry in enumerate(entries):
        priority = entry.get("priority")
        if priority is None:
            raise ValueError(
                f'ERROR: achievements[{idx}] missing required field "priority"'
            )
        if not isinstance(priority, int) or priority not in (1, 2, 3):
            raise ValueError(
                f"ERROR: achievements[{idx}].priority must be 1, 2, or 3 (got {priority})"
            )


def validate(data):
    _check_bullet_priorities("experience", data.get("experience", []))
    _check_bullet_priorities("projects", data.get("projects", []))
    _check_achievement_priorities(data.get("achievements", []))
    ResumeContent.model_validate(data)
