from datetime import datetime

from pydantic import BaseModel, Field


class BrandGuidelineBase(BaseModel):
    name: str
    tone_of_voice: str
    do_list: str
    dont_list: str
    visual_style: str


class BrandGuidelineCreate(BrandGuidelineBase):
    pass


class BrandGuidelineOut(BrandGuidelineBase):
    id: int

    class Config:
        from_attributes = True


class BriefTemplateBase(BaseModel):
    name: str
    channel: str
    structure: str


class BriefTemplateCreate(BriefTemplateBase):
    pass


class BriefTemplateOut(BriefTemplateBase):
    id: int

    class Config:
        from_attributes = True


class PromptLibraryBase(BaseModel):
    name: str
    stage: str
    model_type: str
    prompt_text: str


class PromptLibraryCreate(PromptLibraryBase):
    pass


class PromptLibraryOut(PromptLibraryBase):
    id: int

    class Config:
        from_attributes = True


class MediaSampleBase(BaseModel):
    name: str
    media_type: str
    input_description: str
    output_reference: str
    notes: str


class MediaSampleCreate(MediaSampleBase):
    pass


class MediaSampleOut(MediaSampleBase):
    id: int

    class Config:
        from_attributes = True


class SkillRepositoryBase(BaseModel):
    name: str
    description: str
    entrypoint: str
    config_json: str


class SkillRepositoryCreate(SkillRepositoryBase):
    pass


class SkillRepositoryOut(SkillRepositoryBase):
    id: int

    class Config:
        from_attributes = True


class WorkflowRunRequest(BaseModel):
    objective: str = Field(min_length=3)
    workflow_name: str = "standard-marketing-workflow"
    template_id: int | None = None
    guideline_id: int | None = None
    prompt_id: int | None = None


class WorkflowRunOut(BaseModel):
    id: int
    workflow_name: str
    objective: str
    status: str
    result_json: str
    created_at: datetime

    class Config:
        from_attributes = True
