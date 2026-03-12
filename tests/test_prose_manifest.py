from pathlib import Path

import pytest

from zotero_wordflow.prose_manifest import build_manifest_from_files


def test_build_manifest_from_files_extracts_headings_and_citations(tmp_path: Path) -> None:
    prose = tmp_path / "prose.txt"
    refs = tmp_path / "refs.txt"
    manifest = tmp_path / "manifest.json"
    prose.write_text(
        "2. Background\n\n2.1 Units\n\nText with citations (Jochem et al., 2021; Dark & Bram, 2007).",
        encoding="utf-8",
    )
    refs.write_text(
        "\n".join(
            [
                "Dark, S. J., & Bram, D. (2007). X. Journal. https://doi.org/10.1177/0309133307083294",
                "Jochem, W. C., Leasure, D. R., Pannell, O., Chamberlain, H. R., Jones, P., & Tatem, A. J. (2021). Y. Journal. https://doi.org/10.1177/2399808320921208",
            ]
        ),
        encoding="utf-8",
    )
    payload = build_manifest_from_files(
        text_path=prose,
        references_path=refs,
        collection_name="demo",
        output_manifest_path=manifest,
        output_dir="outputs/run",
        output_docx="outputs/run/out.docx",
        desktop_copy_path=None,
    )
    assert payload["document"]["elements"][0]["type"] == "heading"
    paragraph_segments = payload["document"]["elements"][2]["segments"]
    assert any("citations" in segment for segment in paragraph_segments)


def test_ambiguous_author_year_fails(tmp_path: Path) -> None:
    prose = tmp_path / "prose.txt"
    refs = tmp_path / "refs.txt"
    manifest = tmp_path / "manifest.json"
    prose.write_text("Test paragraph (Smith et al., 2020).", encoding="utf-8")
    refs.write_text(
        "\n".join(
            [
                "Smith, A., Lee, B., & Chen, C. (2020). Paper One. Journal A. https://doi.org/10.1000/one",
                "Smith, A., Lee, B., & Chen, C. (2020). Paper Two. Journal B. https://doi.org/10.1000/two",
            ]
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Ambiguous author-year citations"):
        build_manifest_from_files(
            text_path=prose,
            references_path=refs,
            collection_name="demo",
            output_manifest_path=manifest,
            output_dir="outputs/run",
            output_docx="outputs/run/out.docx",
            desktop_copy_path=None,
        )
