from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any


DOI_PATTERN = re.compile(r"(10\.\d{4,9}/[-._;()/:A-Z0-9]+)", re.IGNORECASE)
YEAR_PATTERN = re.compile(r"\((\d{4}[a-z]?)\)")
HEADING_PATTERN = re.compile(r"^(\d+(?:\.\d+)*\.?)\s+(.+)$")
PAREN_CITATION_PATTERN = re.compile(r"[(\uFF08]([^()\uFF08\uFF09]*\d{4}[a-z]?[^()\uFF08\uFF09]*)[)\uFF09]")


def strip_invisible_prefixes(text: str) -> str:
    return (
        text.replace("\ufeff", "")
        .replace("\u200b", "")
        .replace("\u200c", "")
        .replace("\u200d", "")
        .replace("\u2060", "")
    )


def normalize_space(text: str) -> str:
    cleaned = strip_invisible_prefixes(text)
    return " ".join(cleaned.replace("\u3000", " ").split()).strip()


def normalize_citation_text(text: str) -> str:
    cleaned = normalize_space(text)
    cleaned = cleaned.replace("\uFF08", "(").replace("\uFF09", ")")
    cleaned = cleaned.replace("\uFF0C", ",").replace("\uFF1B", ";")
    cleaned = cleaned.replace(" and ", " & ")
    return cleaned.strip("() ")


def extract_surnames(author_block: str) -> list[str]:
    matches = re.findall(
        r"([^,]+),\s*(?:[A-Z][A-Za-z.-]*)(?:\s+[A-Z][A-Za-z.-]*)*",
        author_block,
    )
    surnames: list[str] = []
    for match in matches:
        surname = re.sub(r"^[&\s]+", "", match).strip()
        if surname:
            surnames.append(surname)
    return surnames


def slug_author_token(author: str) -> str:
    token = re.sub(r"[^A-Za-z0-9]+", "", author)
    return token or "Ref"


def parse_reference_line(line: str, occurrence_count: dict[str, int]) -> dict[str, Any]:
    doi_match = DOI_PATTERN.search(line)
    if not doi_match:
        raise ValueError(f"Reference line missing DOI: {line}")
    doi = doi_match.group(1).rstrip(" .")
    year_match = YEAR_PATTERN.search(line)
    year = int(year_match.group(1)[:4]) if year_match else None
    author_block = normalize_space(line.split("(", 1)[0])
    surnames = extract_surnames(author_block)
    if not surnames:
        surnames = [author_block.split(",")[0].strip() or "Ref"]

    if len(surnames) == 1:
        display_text = f"{surnames[0]}, {year}" if year else surnames[0]
    elif len(surnames) == 2:
        display_text = f"{surnames[0]} & {surnames[1]}, {year}" if year else f"{surnames[0]} & {surnames[1]}"
    else:
        display_text = f"{surnames[0]} et al., {year}" if year else f"{surnames[0]} et al."

    key_base = f"{slug_author_token(surnames[0])}{year or 'NA'}"
    occurrence_count[key_base] = occurrence_count.get(key_base, 0) + 1
    suffix = "" if occurrence_count[key_base] == 1 else chr(ord("a") + occurrence_count[key_base] - 2)
    cite_key = f"{key_base}{suffix}"
    variants = {
        normalize_citation_text(display_text),
        normalize_citation_text(display_text.replace("&", "and")),
        normalize_citation_text(display_text.replace("et al.", "et al")),
    }
    return {
        "cite_key": cite_key,
        "doi": doi.lower(),
        "forced_year": year,
        "variants": tuple(sorted(variants)),
    }


def parse_references(reference_text: str) -> list[dict[str, Any]]:
    lines = [normalize_space(line) for line in reference_text.splitlines() if normalize_space(line)]
    occurrence_count: dict[str, int] = {}
    return [parse_reference_line(line, occurrence_count) for line in lines]


def group_blocks(text: str) -> list[str]:
    clean = strip_invisible_prefixes(text).replace("\r\n", "\n").strip()
    return [strip_invisible_prefixes(block).strip() for block in re.split(r"\n\s*\n", clean) if block.strip()]


def heading_level(numbering: str) -> int:
    return numbering.rstrip(".").count(".") + 1


def build_citation_lookup(references: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = {}
    for ref in references:
        for variant in ref["variants"]:
            buckets.setdefault(variant, []).append(ref)
    ambiguous = {key: refs for key, refs in buckets.items() if len({ref["doi"] for ref in refs}) > 1}
    if ambiguous:
        details = []
        for key, refs in ambiguous.items():
            doi_list = ", ".join(sorted({ref["doi"] for ref in refs}))
            details.append(f"{key} -> {doi_list}")
        raise ValueError(
            "Ambiguous author-year citations found in references. "
            "Disambiguate them manually or use a hand-edited manifest. "
            + " | ".join(details)
        )
    return {key: refs[0] for key, refs in buckets.items()}


def parse_citation_group(content: str, lookup: dict[str, dict[str, Any]]) -> list[dict[str, str]] | None:
    parts = [normalize_citation_text(part) for part in re.split(r"[;\uFF1B]", content) if normalize_citation_text(part)]
    citations: list[dict[str, str]] = []
    for part in parts:
        ref = lookup.get(part)
        if ref is None:
            return None
        citations.append({"cite_key": ref["cite_key"], "display_text": part})
    return citations


def paragraph_to_segments(paragraph: str, lookup: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    segments: list[dict[str, Any]] = []
    cursor = 0
    for match in PAREN_CITATION_PATTERN.finditer(paragraph):
        start, end = match.span()
        if start > cursor:
            segments.append({"text": paragraph[cursor:start]})
        citations = parse_citation_group(match.group(1), lookup)
        if citations is None:
            snippet = paragraph[:120] + ("..." if len(paragraph) > 120 else "")
            raise ValueError(f"Unresolved citation group {match.group(0)!r} in paragraph: {snippet}")
        segments.append({"citations": citations})
        cursor = end
    if cursor < len(paragraph):
        segments.append({"text": paragraph[cursor:]})
    if not segments:
        segments.append({"text": paragraph})
    return segments


def build_document_elements(text: str, references: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lookup = build_citation_lookup(references)
    elements: list[dict[str, Any]] = []
    for block in group_blocks(text):
        block = strip_invisible_prefixes(block)
        heading_match = HEADING_PATTERN.match(block)
        if heading_match and "\n" not in block:
            elements.append({"type": "heading", "level": heading_level(heading_match.group(1)), "text": block})
            continue
        paragraph_text = block.replace("\n", " ").strip()
        elements.append({"type": "paragraph", "segments": paragraph_to_segments(paragraph_text, lookup)})
    return elements


def prepare_manifest_path_value(raw_path: str | None, manifest_output_path: Path) -> str | None:
    if not raw_path:
        return None
    candidate = Path(raw_path).expanduser()
    if candidate.is_absolute():
        return str(candidate.resolve())
    absolute_target = (Path.cwd() / candidate).resolve()
    base_dir = manifest_output_path.parent.resolve()
    try:
        relative_path = os.path.relpath(absolute_target, base_dir)
        return Path(relative_path).as_posix()
    except ValueError:
        return str(absolute_target)


def build_manifest(
    collection_name: str,
    prose_text: str,
    reference_text: str,
    output_dir: str,
    output_docx: str,
    desktop_copy_path: str | None,
) -> dict[str, Any]:
    references = parse_references(reference_text)
    elements = build_document_elements(prose_text, references)
    return {
        "collection_name": collection_name,
        "output_dir": output_dir,
        "output_docx": output_docx,
        "desktop_copy_path": desktop_copy_path,
        "references": [
            {
                "cite_key": ref["cite_key"],
                "doi": ref["doi"],
                **({"forced_year": ref["forced_year"]} if ref["forced_year"] else {}),
            }
            for ref in references
        ],
        "document": {"title": "Generated from natural-language prose", "elements": elements},
    }


def build_manifest_from_files(
    text_path: Path,
    references_path: Path,
    collection_name: str,
    output_manifest_path: Path,
    output_dir: str,
    output_docx: str,
    desktop_copy_path: str | None,
) -> dict[str, Any]:
    prose_text = text_path.read_text(encoding="utf-8-sig")
    reference_text = references_path.read_text(encoding="utf-8-sig")
    return build_manifest(
        collection_name=collection_name,
        prose_text=prose_text,
        reference_text=reference_text,
        output_dir=prepare_manifest_path_value(output_dir, output_manifest_path),
        output_docx=prepare_manifest_path_value(output_docx, output_manifest_path),
        desktop_copy_path=prepare_manifest_path_value(desktop_copy_path, output_manifest_path),
    )
