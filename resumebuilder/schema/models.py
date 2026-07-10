"""Pydantic models for the resume YAML schema."""
import os

import pydantic


class BaseModelWithoutExtraKeys(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")


class SocialNetwork(BaseModelWithoutExtraKeys):
    network: str
    username: str


class Header(BaseModelWithoutExtraKeys):
    name: str
    headline: str | None = None
    location: str | None = None
    email: str | None = None
    phone: str | None = None
    social_networks: list[SocialNetwork] | None = None
    photo: str | None = None


class Bullet(BaseModelWithoutExtraKeys):
    text: str
    priority: int = 1


class EducationEntry(BaseModelWithoutExtraKeys):
    institution: str
    location: str | None = None
    area: str
    degree: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    date: str | None = None
    highlights: list[str] | None = None


class ExperienceEntry(BaseModelWithoutExtraKeys):
    company: str
    position: str
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    date: str | None = None
    summary: str | None = None
    highlights: list[str] | None = None


class NormalEntry(BaseModelWithoutExtraKeys):
    name: str
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    date: str | None = None
    summary: str | None = None
    highlights: list[str] | None = None


class OneLineEntry(BaseModelWithoutExtraKeys):
    label: str
    details: str


class BulletEntry(BaseModelWithoutExtraKeys):
    bullet: str


class ResumeContent(BaseModelWithoutExtraKeys):
    cv: Header
    education: list[EducationEntry] = pydantic.Field(default_factory=list, min_length=1)
    experience: list[ExperienceEntry] = pydantic.Field(default_factory=list)
    projects: list[NormalEntry] = pydantic.Field(default_factory=list)
    skills: list[OneLineEntry] = pydantic.Field(default_factory=list, min_length=1)
    achievements: list[BulletEntry] = pydantic.Field(default_factory=list)

    @pydantic.model_validator(mode="after")
    def check_photo_exists(self):
        if self.cv.photo and not os.path.isfile(os.path.expanduser(self.cv.photo)):
            raise ValueError(f"Photo file not found: {self.cv.photo}")
        return self


Validate = pydantic.TypeAdapter(ResumeContent)
