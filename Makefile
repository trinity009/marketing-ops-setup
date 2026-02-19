.PHONY: setup run test-api extract-brand seed-baseline baseline

setup:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

run:
	cd backend && . .venv/bin/activate && uvicorn app.main:app --reload

test-api:
	bash scripts/test_api.sh

extract-brand:
	cd backend && . .venv/bin/activate && cd .. && python3 brand.py --source-file backend/data/maybelline_source_snippets.txt --output backend/data/maybelline_guidelines_extracted.json

seed-baseline:
	python3 scripts/load_maybelline_baseline.py

baseline: extract-brand seed-baseline
