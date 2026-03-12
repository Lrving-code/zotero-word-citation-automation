from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def citation_code(cite_key: str, display_text: str, item_id: int, uri: str) -> str:
    payload = {
        "citationID": cite_key,
        "properties": {"formattedCitation": display_text, "plainCitation": display_text, "noteIndex": 0},
        "citationItems": [{"id": item_id, "uris": [uri], "itemData": {"id": item_id, "type": "article-journal"}}],
        "schema": "https://github.com/citation-style-language/schema/raw/master/csl-citation.json",
    }
    return " ADDIN ZOTERO_ITEM CSL_CITATION " + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def add_zotero_field(paragraph, item: dict[str, Any], display_text: str) -> None:
    instr = citation_code(item["cite_key"], display_text, item["item_id"], item["uri"])
    run_begin = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    run_begin._r.append(fld_begin)
    for start in range(0, len(instr), 180):
        run_instr = paragraph.add_run()
        instr_text = OxmlElement("w:instrText")
        instr_text.set(qn("xml:space"), "preserve")
        instr_text.text = instr[start : start + 180]
        run_instr._r.append(instr_text)
    run_sep = paragraph.add_run()
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    run_sep._r.append(fld_sep)
    paragraph.add_run(display_text)
    run_end = paragraph.add_run()
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run_end._r.append(fld_end)


def render_document(manifest: dict[str, Any], import_result: dict[str, Any], output_path: Path) -> None:
    zotero_map = {item["cite_key"]: item for item in import_result["items"]}
    doc = Document()
    document_meta = manifest.get("document", {})
    doc.core_properties.title = document_meta.get("title", "Zotero Wordflow Output")
    for element in document_meta.get("elements", []):
        if element["type"] == "heading":
            paragraph = doc.add_paragraph()
            style = "Title" if str(element.get("level")) == "title" else f"Heading {int(element.get('level', 1))}"
            paragraph.style = style
            paragraph.add_run(element["text"])
            continue
        paragraph = doc.add_paragraph()
        for segment in element.get("segments", []):
            if "text" in segment:
                paragraph.add_run(segment["text"])
                continue
            paragraph.add_run(segment.get("prefix", "("))
            for index, entry in enumerate(segment["citations"]):
                if index:
                    paragraph.add_run("; ")
                item = zotero_map[entry["cite_key"]]
                add_zotero_field(paragraph, item, entry["display_text"])
            paragraph.add_run(segment.get("suffix", ")"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)
