#!/usr/bin/env python3
"""
Extract and structure brand guidelines from a beauty brand website.

Modes:
1) Live crawl mode: fetches pages from a starting URL.
2) Source-file mode: parses pre-collected snippets from a text file.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin, urlparse

KEYWORDS = (
    "about",
    "mission",
    "values",
    "change",
    "impact",
    "conscious",
    "sustainability",
    "diversity",
    "inclusion",
)


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_page_text(html: str) -> list[str]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    blocks: list[str] = []
    for tag in soup.find_all(["h1", "h2", "h3", "p", "li"]):
        text = clean_text(tag.get_text(" "))
        if len(text) >= 30:
            blocks.append(text)
    return blocks


def crawl_site(start_url: str, max_pages: int = 8) -> list[dict]:
    import requests
    from bs4 import BeautifulSoup

    domain = urlparse(start_url).netloc
    visited: set[str] = set()
    queue = [start_url]
    pages: list[dict] = []

    while queue and len(visited) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            response = requests.get(url, timeout=12)
            response.raise_for_status()
        except requests.RequestException:
            continue

        blocks = extract_page_text(response.text)
        if blocks:
            pages.append({"source": url, "blocks": blocks[:80]})

        soup = BeautifulSoup(response.text, "html.parser")
        for anchor in soup.find_all("a", href=True):
            next_url = urljoin(url, anchor["href"])
            parsed = urlparse(next_url)
            if parsed.netloc != domain:
                continue
            lowered = next_url.lower()
            if any(word in lowered for word in KEYWORDS) and next_url not in visited:
                queue.append(next_url)

    return pages


def parse_source_file(path: Path) -> list[dict]:
    pages: list[dict] = []
    source = ""
    blocks: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Source:"):
            if source and blocks:
                pages.append({"source": source, "blocks": blocks})
            source = line.replace("Source:", "", 1).strip()
            blocks = []
            continue
        if line.strip().startswith("- "):
            blocks.append(line.strip()[2:])
    if source and blocks:
        pages.append({"source": source, "blocks": blocks})
    return pages


def structure_guidelines(brand: str, pages: list[dict]) -> dict:
    all_blocks: list[str] = []
    for page in pages:
        all_blocks.extend(page["blocks"])

    joined = " ".join(all_blocks).lower()
    tone_candidates = []
    if "new york" in joined:
        tone_candidates.append("Urban")
    if "fast" in joined or "easy" in joined:
        tone_candidates.append("Fast-moving")
    if "inclusive" in joined or "diversity" in joined or "every" in joined:
        tone_candidates.append("Inclusive")
    if "high-performance" in joined or "performance" in joined:
        tone_candidates.append("Performance-led")
    if "confidence" in joined or "self-expression" in joined:
        tone_candidates.append("Empowering")

    keyword_counter = Counter()
    tracked = [
        "innovation",
        "accessible",
        "effortless",
        "inclusive",
        "diversity",
        "self-expression",
        "sustainability",
        "recycling",
        "anxiety",
        "depression",
        "performance",
    ]
    for key in tracked:
        keyword_counter[key] = joined.count(key)

    pillars = [
        f"{k}: highlighted in source copy"
        for k, count in keyword_counter.items()
        if count > 0
    ]

    return {
        "brand": brand,
        "extracted_on": "2026-02-19",
        "tone_of_voice": ", ".join(tone_candidates) or "Confident, practical, inclusive",
        "do_list": [
            "Lead with product performance proof in real-life use.",
            "Use inclusive casting and shade/skin diversity across creative.",
            "Anchor messaging in direct, energetic, urban language.",
            "Include social impact or sustainability references when relevant.",
        ],
        "dont_list": [
            "Avoid vague luxury language that hides product utility.",
            "Avoid narrow representation in visual and copy examples.",
            "Avoid claims without context, proof point, or source.",
        ],
        "visual_style": [
            "High-contrast beauty closeups",
            "City-inspired backgrounds and motion",
            "Product-first framing with tactile swatches",
        ],
        "brand_pillars": pillars,
        "source_pages": [p["source"] for p in pages],
        "source_highlights": all_blocks[:25],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Brand guideline extractor")
    parser.add_argument("--brand", default="Maybelline New York")
    parser.add_argument("--url", default="https://www.maybelline.com/about-maybelline")
    parser.add_argument("--max-pages", type=int, default=8)
    parser.add_argument("--source-file", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("backend/data/maybelline_guidelines_extracted.json"),
    )
    args = parser.parse_args()

    if args.source_file:
        pages = parse_source_file(args.source_file)
    else:
        pages = crawl_site(args.url, max_pages=args.max_pages)

    if not pages:
        raise SystemExit("No source content parsed; check network or source file.")

    guideline = structure_guidelines(args.brand, pages)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(guideline, indent=2), encoding="utf-8")
    print(f"Wrote structured guideline JSON to {args.output}")


if __name__ == "__main__":
    main()
