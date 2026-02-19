from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from .models import BrandGuideline, BriefTemplate, MediaSample, PromptLibrary, SkillRepository


def _load_extracted_guideline() -> dict:
    path = Path(__file__).resolve().parents[1] / "data" / "maybelline_guidelines_extracted.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "tone_of_voice": "Urban, Inclusive, Performance-led, Empowering",
        "do_list": [
            "Lead with proof-based product performance",
            "Use inclusive representation in tone and visuals",
            "Keep copy concise and energetic",
        ],
        "dont_list": [
            "Avoid generic beauty claims without proof",
            "Avoid exclusive or narrow definitions of beauty",
        ],
        "visual_style": [
            "High-contrast product shots",
            "NYC-inspired motion and settings",
            "Texture-focused beauty closeups",
        ],
        "source_pages": [
            "https://www.maybelline.com/about-maybelline",
            "https://www.maybelline.com/make-up-make-change",
            "https://www.maybelline.com/conscious-together",
        ],
    }


def bootstrap_maybelline_baseline(db: Session) -> dict:
    extracted = _load_extracted_guideline()

    guideline_name = "Maybelline NYC Core Guideline (Baseline)"
    if not db.query(BrandGuideline).filter(BrandGuideline.name == guideline_name).first():
        db.add(
            BrandGuideline(
                name=guideline_name,
                tone_of_voice=extracted.get("tone_of_voice", "Urban, Inclusive, Performance-led"),
                do_list="\n".join(extracted.get("do_list", [])),
                dont_list="\n".join(extracted.get("dont_list", [])),
                visual_style="\n".join(extracted.get("visual_style", [])),
            )
        )

    templates = [
        (
            "Maybelline Paid Social 15s Video Brief",
            "paid-social",
            (
                "Objective | Audience | Product focus | Hook (0-3s) | Demo/proof (4-9s) | "
                "Benefit recap (10-13s) | CTA (14-15s) | Mandatory claims"
            ),
        ),
        (
            "Maybelline PDP Hero Image Brief",
            "ecommerce",
            (
                "SKU | Shade | Key benefit | Framing specs | Background style | Overlay text | "
                "Alt text | Compliance checks"
            ),
        ),
        (
            "Maybelline CRM Launch Brief",
            "email-crm",
            (
                "Campaign objective | Segment | Subject line variants | Offer logic | "
                "Primary visual | Body copy modules | CTA hierarchy | Measurement plan"
            ),
        ),
    ]
    for name, channel, structure in templates:
        if not db.query(BriefTemplate).filter(BriefTemplate.name == name).first():
            db.add(BriefTemplate(name=name, channel=channel, structure=structure))

    prompts = [
        (
            "Maybelline Video Hook Generator",
            "copy-generation",
            "text",
            (
                "Generate 10 beauty ad hooks under 7 words each. Must include a performance angle, "
                "urban energy, and inclusive tone. Avoid generic luxury language."
            ),
        ),
        (
            "Maybelline UGC Script Prompt",
            "content-production",
            "text-video",
            (
                "Write a 15-second UGC script with timestamped beats, on-screen text, and proof-first "
                "messaging for a long-wear lip product."
            ),
        ),
        (
            "Maybelline PDP Copy Prompt",
            "commerce-content",
            "text",
            (
                "Draft a product page hero headline, 3 benefit bullets, and one substantiated claim line "
                "for a beauty SKU with shade context."
            ),
        ),
        (
            "Maybelline Image Generation Prompt",
            "creative-production",
            "image",
            (
                "Create a high-contrast product beauty shot in a NYC-inspired environment with inclusive cast, "
                "showing texture detail and clear packshot hierarchy."
            ),
        ),
        (
            "Maybelline 6s Bumper Video Prompt",
            "creative-production",
            "video",
            (
                "Generate a 6-second bumper: 1s hook, 3s transformation/demo, 2s brand mnemonic and CTA. "
                "Prioritize legibility for vertical mobile feed."
            ),
        ),
        (
            "Maybelline Voiceover Prompt",
            "creative-production",
            "audio",
            (
                "Write a 12-second VO script in energetic, inclusive tone with one claim line, one sensory line, "
                "and one direct CTA."
            ),
        ),
    ]
    for name, stage, model_type, prompt_text in prompts:
        if not db.query(PromptLibrary).filter(PromptLibrary.name == name).first():
            db.add(
                PromptLibrary(
                    name=name,
                    stage=stage,
                    model_type=model_type,
                    prompt_text=prompt_text,
                )
            )

    media = [
        (
            "Mock Brand Styleboard",
            "image",
            "Input: Brand moodboard request with urban inclusive performance-led positioning",
            "assets/maybelline_mock_styleboard.svg",
            "Synthetic baseline styleboard generated for local testing.",
        ),
        (
            "Official About Page Visual Reference",
            "image",
            "Input: Hero image benchmark for website storytelling",
            "https://www.maybelline.com/about-maybelline",
            "Public brand page used as visual direction reference.",
        ),
        (
            "Public Video Ad Reference",
            "video",
            "Input: 15-second product demo ad benchmark",
            "https://www.youtube.com/watch?v=fTH6R4fkQhA",
            "Publicly available YouTube format reference for short-form sequencing.",
        ),
        (
            "Public Audio Spot Reference",
            "audio",
            "Input: 10-15 second beauty promo VO benchmark",
            "https://www.youtube.com/results?search_query=maybelline+commercial",
            "Public query link for collecting current beauty audio/voiceover pacing references.",
        ),
    ]
    for name, media_type, input_description, output_reference, notes in media:
        if not db.query(MediaSample).filter(MediaSample.name == name).first():
            db.add(
                MediaSample(
                    name=name,
                    media_type=media_type,
                    input_description=input_description,
                    output_reference=output_reference,
                    notes=notes,
                )
            )

    skills = [
        (
            "research-agent-maybelline",
            "Brand and category research agent profile for beauty campaigns",
            "agents.research_agent",
            {"sources": extracted.get("source_pages", [])},
        ),
        (
            "insights-agent-maybelline",
            "Insights synthesis profile tuned for campaign hypothesis generation",
            "agents.insights_agent",
            {"focus": ["performance claims", "audience resonance", "format testing"]},
        ),
        (
            "content-agent-maybelline",
            "Content generation profile for paid + commerce creative",
            "agents.content_agent",
            {"formats": ["paid-social-video", "pdp-image", "crm-copy"]},
        ),
    ]
    for name, description, entrypoint, config in skills:
        if not db.query(SkillRepository).filter(SkillRepository.name == name).first():
            db.add(
                SkillRepository(
                    name=name,
                    description=description,
                    entrypoint=entrypoint,
                    config_json=json.dumps(config),
                )
            )

    db.commit()
    return {"status": "maybelline-baseline-loaded"}
