from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def resolve_path(base_dir: Path, raw_path: str | None) -> Path | None:
    if not raw_path:
        return None
    candidate = Path(raw_path).expanduser()
    if candidate.is_absolute():
        return candidate
    return (base_dir / candidate).resolve()


def validate_manifest(manifest: dict[str, Any]) -> None:
    required_top = ("collection_name", "output_dir", "output_docx", "references", "document")
    missing_top = [key for key in required_top if key not in manifest]
    if missing_top:
        raise ValueError(f"Manifest missing required keys: {missing_top}")

    known_refs = {ref["cite_key"] for ref in manifest["references"]}
    if not known_refs:
        raise ValueError("Manifest must include at least one reference.")

    for ref in manifest["references"]:
        if "cite_key" not in ref or "doi" not in ref:
            raise ValueError(f"Reference entry missing cite_key or doi: {ref}")

    for index, element in enumerate(manifest["document"].get("elements", [])):
        element_type = element.get("type")
        if element_type == "heading":
            if "text" not in element or "level" not in element:
                raise ValueError(f"Heading element {index} missing text or level.")
            continue
        if element_type != "paragraph":
            raise ValueError(f"Unsupported element type at index {index}: {element_type}")
        for segment in element.get("segments", []):
            if "text" in segment:
                continue
            if "citations" not in segment:
                raise ValueError(f"Paragraph element {index} has a non-text segment without citations.")
            for citation in segment["citations"]:
                cite_key = citation.get("cite_key")
                if cite_key not in known_refs:
                    raise ValueError(f"Citation cite_key not found in references: {cite_key}")
                if "display_text" not in citation:
                    raise ValueError(f"Citation missing display_text: {citation}")
