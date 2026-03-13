from __future__ import annotations

from pathlib import Path
from typing import Any

import requests

from .models import ReferenceSeed


USER_AGENT = "zotero-wordflow/0.1.3 (mailto:local@example.com)"


def normalize_title(title: str) -> str:
    return " ".join(title.split()).strip()


def fetch_crossref_metadata(seed: ReferenceSeed) -> dict[str, Any]:
    response = requests.get(
        f"https://api.crossref.org/works/{seed.doi}",
        headers={"User-Agent": USER_AGENT},
        timeout=30,
    )
    response.raise_for_status()
    message = response.json()["message"]
    authors = []
    for author in message.get("author", []):
        given = author.get("given", "").strip()
        family = author.get("family", "").strip()
        if not given and not family:
            family = author.get("name", "").strip()
        if given or family:
            authors.append({"given": given, "family": family})

    issued_year = None
    if message.get("published-print", {}).get("date-parts"):
        issued_year = message["published-print"]["date-parts"][0][0]
    elif message.get("issued", {}).get("date-parts"):
        issued_year = message["issued"]["date-parts"][0][0]

    year = seed.forced_year or issued_year
    if year is None:
        raise ValueError(f"Unable to determine year for DOI {seed.doi}")

    return {
        "cite_key": seed.cite_key,
        "doi": seed.doi.lower(),
        "title": normalize_title(" ".join(message.get("title", []))),
        "journal": normalize_title(" ".join(message.get("container-title", []))),
        "year": int(year),
        "volume": message.get("volume") or "",
        "issue": message.get("issue") or "",
        "pages": message.get("page") or "",
        "url": message.get("URL") or f"https://doi.org/{seed.doi.lower()}",
        "authors": authors,
    }


def write_ris(refs: list[dict[str, Any]], output_path: Path) -> None:
    lines: list[str] = []
    for ref in refs:
        lines.append("TY  - JOUR")
        for author in ref["authors"]:
            lines.append(f"AU  - {author['family']}, {author['given']}".strip().strip(","))
        lines.extend(
            [
                f"TI  - {ref['title']}",
                f"JO  - {ref['journal']}",
                f"PY  - {ref['year']}",
                f"DO  - {ref['doi']}",
                f"UR  - {ref['url']}",
                "ER  - ",
                "",
            ]
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
