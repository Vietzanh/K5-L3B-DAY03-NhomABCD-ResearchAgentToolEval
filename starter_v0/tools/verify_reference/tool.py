from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote, unquote, urlparse

import requests

from tools._shared import TIMEOUT, err

TOOL_NAME = "verify_reference"
CROSSREF_WORKS_URL = "https://api.crossref.org/works"
DOI_PATTERN = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
MAX_REFERENCE_LENGTH = 500


def _normalize_doi(reference: str) -> str | None:
    value = reference.strip()
    if value.lower().startswith("doi:"):
        value = value[4:].strip()
    elif value.lower().startswith(("https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "http://dx.doi.org/")):
        value = unquote(urlparse(value).path.lstrip("/"))

    return value if DOI_PATTERN.fullmatch(value) else None


def _format_work(work: dict[str, Any]) -> dict[str, Any]:
    date_parts = (work.get("published") or work.get("published-print") or work.get("created") or {}).get("date-parts") or []
    year = date_parts[0][0] if date_parts and date_parts[0] else None
    authors = [
        " ".join(part for part in (author.get("given"), author.get("family")) if part)
        for author in work.get("author", [])
    ]
    titles = work.get("title") or []
    doi = work.get("DOI")
    return {
        "doi": doi,
        "title": titles[0] if titles else None,
        "authors": authors,
        "year": year,
        "publisher": work.get("publisher"),
        "url": work.get("URL") or (f"https://doi.org/{doi}" if doi else None),
        "type": work.get("type"),
    }


def verify_reference(reference: str = "") -> dict[str, Any]:
    """Check whether Crossref has a publication record for a DOI or title."""
    if not isinstance(reference, str) or not reference.strip():
        return {
            "tool": TOOL_NAME,
            "found": False,
            "match_type": None,
            "query": reference if isinstance(reference, str) else None,
            "items": [],
            "message": "Provide a DOI or publication title to check in Crossref.",
        }
    if len(reference) > MAX_REFERENCE_LENGTH:
        return {
            "tool": TOOL_NAME,
            "error": "ValueError",
            "message": f"reference must be at most {MAX_REFERENCE_LENGTH} characters.",
        }

    try:
        doi = _normalize_doi(reference)
        if doi:
            response = requests.get(
                f"{CROSSREF_WORKS_URL}/{quote(doi, safe='/')}",
                headers={"User-Agent": "ResearchAgentToolEval/1.0"},
                timeout=TIMEOUT,
            )
            if response.status_code == 404:
                return {
                    "tool": TOOL_NAME,
                    "found": False,
                    "match_type": "doi",
                    "query": reference,
                    "items": [],
                    "source": "Crossref",
                }
            response.raise_for_status()
            payload = response.json()
            work = payload.get("message") or {}
            items = [_format_work(work)] if work else []
            return {
                "tool": TOOL_NAME,
                "found": bool(items),
                "match_type": "doi",
                "query": reference,
                "items": items,
                "source": "Crossref",
            }

        response = requests.get(
            CROSSREF_WORKS_URL,
            params={"query.bibliographic": reference.strip(), "rows": 3},
            headers={"User-Agent": "ResearchAgentToolEval/1.0"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        works = (payload.get("message") or {}).get("items") or []
        items = [_format_work(work) for work in works if isinstance(work, dict)]
        return {
            "tool": TOOL_NAME,
            "found": bool(items),
            "match_type": "title_search",
            "query": reference.strip(),
            "items": items,
            "source": "Crossref",
            "note": "A title search result is a possible match; confirm the title and authors before citing.",
        }
    except Exception as exc:
        return err(TOOL_NAME, exc)
