from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .agents import orchestrate_workflow
from .database import Base, engine, get_db
from .models import BrandGuideline, BriefTemplate, MediaSample, PromptLibrary, SkillRepository, WorkflowRun
from .seed_data import bootstrap_maybelline_baseline
from .schemas import (
    BrandGuidelineCreate,
    BrandGuidelineOut,
    BriefTemplateCreate,
    BriefTemplateOut,
    MediaSampleCreate,
    MediaSampleOut,
    PromptLibraryCreate,
    PromptLibraryOut,
    SkillRepositoryCreate,
    SkillRepositoryOut,
    WorkflowRunOut,
    WorkflowRunRequest,
)

app = FastAPI(title="Marketing Ops Setup System", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR)), name="assets")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": "marketing-ops-setup"}


@app.get("/", include_in_schema=False)
def root() -> FileResponse:
    index_file = FRONTEND_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    return FileResponse(index_file)


@app.get("/api/brand-guidelines", response_model=list[BrandGuidelineOut])
def list_brand_guidelines(db: Session = Depends(get_db)):
    return db.query(BrandGuideline).all()


@app.post("/api/brand-guidelines", response_model=BrandGuidelineOut)
def create_brand_guideline(payload: BrandGuidelineCreate, db: Session = Depends(get_db)):
    row = BrandGuideline(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.get("/api/brief-templates", response_model=list[BriefTemplateOut])
def list_brief_templates(db: Session = Depends(get_db)):
    return db.query(BriefTemplate).all()


@app.post("/api/brief-templates", response_model=BriefTemplateOut)
def create_brief_template(payload: BriefTemplateCreate, db: Session = Depends(get_db)):
    row = BriefTemplate(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.get("/api/prompt-libraries", response_model=list[PromptLibraryOut])
def list_prompt_libraries(db: Session = Depends(get_db)):
    return db.query(PromptLibrary).all()


@app.post("/api/prompt-libraries", response_model=PromptLibraryOut)
def create_prompt_library(payload: PromptLibraryCreate, db: Session = Depends(get_db)):
    row = PromptLibrary(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.get("/api/media-samples", response_model=list[MediaSampleOut])
def list_media_samples(db: Session = Depends(get_db)):
    return db.query(MediaSample).all()


@app.post("/api/media-samples", response_model=MediaSampleOut)
def create_media_sample(payload: MediaSampleCreate, db: Session = Depends(get_db)):
    row = MediaSample(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.get("/api/skill-repositories", response_model=list[SkillRepositoryOut])
def list_skill_repositories(db: Session = Depends(get_db)):
    return db.query(SkillRepository).all()


@app.post("/api/skill-repositories", response_model=SkillRepositoryOut)
def create_skill_repository(payload: SkillRepositoryCreate, db: Session = Depends(get_db)):
    row = SkillRepository(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.post("/api/workflows/run", response_model=WorkflowRunOut)
def run_workflow(payload: WorkflowRunRequest, db: Session = Depends(get_db)):
    guideline = None
    template = None
    prompt = None

    if payload.guideline_id:
        row = db.get(BrandGuideline, payload.guideline_id)
        if not row:
            raise HTTPException(status_code=404, detail="Brand guideline not found")
        guideline = row.tone_of_voice

    if payload.template_id:
        row = db.get(BriefTemplate, payload.template_id)
        if not row:
            raise HTTPException(status_code=404, detail="Brief template not found")
        template = row.structure

    if payload.prompt_id:
        row = db.get(PromptLibrary, payload.prompt_id)
        if not row:
            raise HTTPException(status_code=404, detail="Prompt library item not found")
        prompt = row.prompt_text

    result_json = orchestrate_workflow(
        objective=payload.objective,
        guideline=guideline,
        template=template,
        prompt=prompt,
    )

    run = WorkflowRun(
        workflow_name=payload.workflow_name,
        objective=payload.objective,
        status="completed",
        result_json=result_json,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


@app.get("/api/workflows", response_model=list[WorkflowRunOut])
def list_workflows(db: Session = Depends(get_db)):
    return db.query(WorkflowRun).order_by(WorkflowRun.id.desc()).all()


@app.post("/api/setup/bootstrap")
def bootstrap(db: Session = Depends(get_db)):
    if not db.query(BrandGuideline).first():
        db.add(
            BrandGuideline(
                name="Primary Brand",
                tone_of_voice="Confident, clear, practical",
                do_list="Use concrete outcomes, proof points, and direct CTAs",
                dont_list="Avoid vague claims and heavy jargon",
                visual_style="Clean, product-forward visuals with strong contrast",
            )
        )
    if not db.query(BriefTemplate).first():
        db.add(
            BriefTemplate(
                name="Paid Social Conversion Brief",
                channel="paid-social",
                structure="Objective, audience, offer, proof, CTA, asset specs",
            )
        )
    if not db.query(PromptLibrary).first():
        db.add(
            PromptLibrary(
                name="Awareness to Conversion Copy",
                stage="copy-generation",
                model_type="text",
                prompt_text="Write 3 ad variants with hook, value proposition, and CTA.",
            )
        )
    if not db.query(MediaSample).first():
        db.add(
            MediaSample(
                name="Lifestyle Image Benchmark",
                media_type="image",
                input_description="User with product in a bright workspace",
                output_reference="/samples/lifestyle-output.jpg",
                notes="Prioritize natural lighting and clear product framing",
            )
        )
    if not db.query(SkillRepository).first():
        db.add(
            SkillRepository(
                name="research-agent",
                description="Agent profile for competitor and audience research",
                entrypoint="agents.research_agent",
                config_json='{"source_priority": ["crm", "ads", "market"]}',
            )
        )
    db.commit()
    return {"status": "bootstrapped"}


@app.post("/api/setup/bootstrap-maybelline")
def bootstrap_maybelline(db: Session = Depends(get_db)):
    return bootstrap_maybelline_baseline(db)
