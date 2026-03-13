from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from zotero_wordflow.cli import build_parser, from_text_command


def test_from_text_command_builds_manifest_then_runs(tmp_path: Path) -> None:
    prose = tmp_path / "prose.txt"
    refs = tmp_path / "refs.txt"
    manifest = tmp_path / "manifest.json"
    prose.write_text(
        "\ufeffText with citations (Boscoe et al., 2012).",
        encoding="utf-8-sig",
    )
    refs.write_text(
        "\ufeffBoscoe, F. P., Henry, K. A., & Zdeb, M. S. (2012). X. Journal. https://doi.org/10.1080/00330124.2011.583586",
        encoding="utf-8-sig",
    )
    args = SimpleNamespace(
        text=str(prose),
        references=str(refs),
        collection_name="demo refs",
        output_manifest=str(manifest),
        output_dir="outputs/run",
        output_docx="outputs/run/out.docx",
        desktop_copy_path=None,
    )

    with patch("zotero_wordflow.cli.run_from_manifest", return_value={"output_docx": tmp_path / "out.docx"}) as run_mock:
        status = from_text_command(args)

    assert status == 0
    assert manifest.exists()
    run_mock.assert_called_once_with(manifest.resolve())


def test_parser_includes_from_text_command() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "from-text",
            "--text",
            "prose.txt",
            "--references",
            "refs.txt",
            "--collection-name",
            "demo refs",
            "--output-manifest",
            "manifest.json",
            "--output-dir",
            "run",
            "--output-docx",
            "out.docx",
        ]
    )
    assert args.command == "from-text"
