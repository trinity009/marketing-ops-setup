from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class BrandGuideline(Base):
    __tablename__ = "brand_guidelines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    tone_of_voice: Mapped[str] = mapped_column(Text)
    do_list: Mapped[str] = mapped_column(Text)
    dont_list: Mapped[str] = mapped_column(Text)
    visual_style: Mapped[str] = mapped_column(Text)


class BriefTemplate(Base):
    __tablename__ = "brief_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    channel: Mapped[str] = mapped_column(String(80), index=True)
    structure: Mapped[str] = mapped_column(Text)


class PromptLibrary(Base):
    __tablename__ = "prompt_libraries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    stage: Mapped[str] = mapped_column(String(80), index=True)
    model_type: Mapped[str] = mapped_column(String(80), index=True)
    prompt_text: Mapped[str] = mapped_column(Text)


class MediaSample(Base):
    __tablename__ = "media_samples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    media_type: Mapped[str] = mapped_column(String(40), index=True)
    input_description: Mapped[str] = mapped_column(Text)
    output_reference: Mapped[str] = mapped_column(Text)
    notes: Mapped[str] = mapped_column(Text)


class SkillRepository(Base):
    __tablename__ = "skill_repositories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text)
    entrypoint: Mapped[str] = mapped_column(String(160))
    config_json: Mapped[str] = mapped_column(Text)


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workflow_name: Mapped[str] = mapped_column(String(120), index=True)
    objective: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), index=True)
    result_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
