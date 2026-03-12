from pathlib import Path

from zotero_wordflow.manifest import resolve_path, validate_manifest


def test_resolve_relative_path_against_manifest_dir(tmp_path: Path) -> None:
    manifest_dir = tmp_path / "a" / "b"
    manifest_dir.mkdir(parents=True)
    resolved = resolve_path(manifest_dir, "outputs/demo.docx")
    assert resolved == (manifest_dir / "outputs" / "demo.docx").resolve()


def test_validate_manifest_accepts_minimal_structure() -> None:
    manifest = {
        "collection_name": "demo",
        "output_dir": "outputs",
        "output_docx": "outputs/demo.docx",
        "references": [{"cite_key": "Jochem2021", "doi": "10.1177/2399808320921208"}],
        "document": {
            "elements": [
                {
                    "type": "paragraph",
                    "segments": [
                        {"text": "Example "},
                        {"citations": [{"cite_key": "Jochem2021", "display_text": "Jochem et al., 2021"}]},
                    ],
                }
            ]
        },
    }
    validate_manifest(manifest)
