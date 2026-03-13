from pathlib import Path
from zipfile import ZipFile

from zotero_wordflow.docx_fields import render_document


def document_xml(path: Path) -> str:
    with ZipFile(path) as archive:
        return archive.read("word/document.xml").decode("utf-8")


def test_parenthetical_group_renders_as_single_zotero_field(tmp_path: Path) -> None:
    output_path = tmp_path / "group.docx"
    manifest = {
        "document": {
            "title": "demo",
            "elements": [
                {
                    "type": "paragraph",
                    "segments": [
                        {"text": "Example "},
                        {
                            "prefix": "(",
                            "suffix": ")",
                            "citations": [
                                {"cite_key": "Corbane2019", "display_text": "Corbane et al., 2019"},
                                {"cite_key": "Marconcini2020", "display_text": "Marconcini et al., 2020"},
                            ],
                        },
                    ],
                }
            ],
        }
    }
    import_result = {
        "items": [
            {"cite_key": "Corbane2019", "item_id": 1, "uri": "u1"},
            {"cite_key": "Marconcini2020", "item_id": 2, "uri": "u2"},
        ]
    }

    render_document(manifest, import_result, output_path)
    xml = document_xml(output_path)

    assert xml.count("ADDIN ZOTERO_ITEM CSL_CITATION") == 1
    assert '"citationID":"Corbane2019_Marconcini2020"' in xml
    assert '"id":1,"uris":["u1"],"itemData":{"id":1,"type":"article-journal"}' in xml
    assert '"id":2,"uris":["u2"]' in xml
    assert '"type":"article-journal"}}]' in xml
    assert "<w:t>(Corbane et al., 2019; Marconcini et al., 2020)</w:t>" in xml


def test_narrative_citation_renders_with_suppress_author(tmp_path: Path) -> None:
    output_path = tmp_path / "narrative.docx"
    manifest = {
        "document": {
            "title": "demo",
            "elements": [
                {
                    "type": "paragraph",
                    "segments": [
                        {"text": "Smith "},
                        {
                            "prefix": "(",
                            "suffix": ")",
                            "citations": [
                                {"cite_key": "Smith2020", "display_text": "2020", "suppress_author": True},
                            ],
                        },
                        {"text": " argues the point."},
                    ],
                }
            ],
        }
    }
    import_result = {"items": [{"cite_key": "Smith2020", "item_id": 9, "uri": "u9"}]}

    render_document(manifest, import_result, output_path)
    xml = document_xml(output_path)

    assert xml.count("ADDIN ZOTERO_ITEM CSL_CITATION") == 1
    assert '"suppressAuthor":true' in xml
    assert 'xml:space="preserve">Smith </w:t>' in xml
    assert "<w:t>(2020)</w:t>" in xml
