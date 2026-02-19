import json


def research_agent(objective: str, guideline: str | None) -> dict:
    sources = [
        "Owned analytics trend summary",
        "Paid campaign CTR variance",
        "Competitor messaging snapshot",
    ]
    return {
        "objective": objective,
        "brand_constraints": guideline or "No guideline supplied",
        "research_findings": [
            "Audience engagement increases on clear value statements in first 2 lines.",
            "Short-form visual-led formats outperform static posts in conversion campaigns.",
            "Lifecycle messaging performs best when segmented by first vs repeat purchase intent.",
        ],
        "sources_checked": sources,
    }


def insights_agent(research_payload: dict) -> dict:
    findings = research_payload.get("research_findings", [])
    insight = " ".join(findings[:2])
    return {
        "priority_insight": insight,
        "recommended_test_matrix": [
            "Hook variant A/B",
            "Offer framing A/B",
            "Format split: image vs short video",
        ],
    }


def content_agent(objective: str, template: str | None, prompt: str | None, insight: str) -> dict:
    structure = template or "Goal, audience, key message, CTA"
    prompt_basis = prompt or "Write concise conversion-first copy"
    copy = (
        f"Objective: {objective}\n"
        f"Structure: {structure}\n"
        f"Guidance: {prompt_basis}\n"
        f"Core Insight: {insight}\n"
        "Draft: Discover a faster way to achieve your goal with a focused offer, clear proof, and a direct CTA."
    )
    return {
        "draft_copy": copy,
        "asset_notes": "Pair with high-contrast product-focused creative and one social-proof callout.",
    }


def orchestrate_workflow(objective: str, guideline: str | None, template: str | None, prompt: str | None) -> str:
    research = research_agent(objective, guideline)
    insights = insights_agent(research)
    content = content_agent(
        objective=objective,
        template=template,
        prompt=prompt,
        insight=insights["priority_insight"],
    )
    payload = {
        "research": research,
        "insights": insights,
        "content": content,
    }
    return json.dumps(payload, indent=2)
