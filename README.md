# Marketing Ops Setup System (MVP)

This repository now contains a full starter system for marketing + commerce operations:

- Backend API (`FastAPI` + `SQLite`) for a structured knowledge base.
- Frontend dashboard (HTML/CSS/JS) for setup and workflow execution.
- Sub-task-specific agents (`research`, `insights`, `content`) orchestrated into one workflow.
- Repository entity to register skills/agent configs.

## Project structure

- `backend/app/main.py`: API routes and workflow execution.
- `backend/app/models.py`: database schema for guidelines, templates, prompts, media samples, skills, and workflow runs.
- `backend/app/agents.py`: agent modules and orchestrator.
- `frontend/index.html`: dashboard UI.
- `frontend/app.js`: API integration and actions.

## Run locally

```bash
make setup
make run
```

Open `http://127.0.0.1:8000`.

## Load Maybelline baseline KB

This repo includes a baseline beauty-brand dataset (Maybelline New York theme) with:

- extracted brand-guideline JSON
- mock styleboard image
- brief templates for paid social, ecommerce PDP, and CRM
- prompt library entries for text/image/video/audio workflows
- public media/ad reference links

Generate structured brand guideline file:

```bash
make extract-brand
```

Seed baseline records into the knowledge base:

```bash
make seed-baseline
```

Or run both:

```bash
make baseline
```

## One-command API smoke test

Run this from repo root:

```bash
make test-api
```

What it does:

- starts the API in the background
- checks `/api/health`
- bootstraps sample KB data
- runs one workflow
- loads Maybelline baseline KB
- fetches workflow history
- shuts the API down

## Hosted deployment (Render)

This project includes `Dockerfile` and `render.yaml`.

1. Push this repo to GitHub.
2. In Render, create a new Blueprint/Web Service from the repo.
3. Render will detect `render.yaml` and build using Docker.
4. After deploy completes, Render provides your public URL (for example `https://your-service.onrender.com`).

Use this endpoint once live to preload baseline data:

```bash
curl -X POST https://YOUR-RENDER-URL/api/setup/bootstrap-maybelline
```

## Brand extraction script

`brand.py` supports:

- Live crawl mode (needs internet):
  - `python3 brand.py --url https://www.maybelline.com/about-maybelline`
- Offline source mode:
  - `python3 brand.py --source-file backend/data/maybelline_source_snippets.txt`

Output file:

- `backend/data/maybelline_guidelines_extracted.json`

## What this MVP already supports

- Create and list:
  - brand guidelines
  - brief templates
  - prompt library items
  - media samples
  - skill repository entries
- Bootstrap sample KB data.
- Run a workflow that chains research -> insights -> content generation.
- Persist workflow runs for auditability.

## Next production steps

1. Add auth + role-based access control.
2. Replace local agent logic with real model providers (OpenAI, Claude, image/video endpoints).
3. Add vector search and document ingestion pipeline for brand and campaign docs.
4. Add asset upload storage (S3/GCS) for sample input/output files.
5. Add queueing + async workers for long-running multimedia tasks.
