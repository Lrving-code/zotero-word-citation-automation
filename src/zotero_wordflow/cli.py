from __future__ import annotations

import argparse
from pathlib import Path

from .docx_fields import render_document
from .doi_verify import fetch_crossref_metadata, write_ris
from .manifest import load_json, resolve_path, validate_manifest, write_json
from .models import ReferenceSeed
from .prose_manifest import build_manifest_from_files
from .windows_paths import DEFAULT_LOCAL_USER_KEY, DEFAULT_ZOTERO_DATA_DIR, DEFAULT_ZOTERO_EXE
from .zotero_import import backup_zotero_db, import_to_zotero, restore_zotero_db, start_zotero, stop_zotero


def run_from_manifest(manifest_path: Path) -> dict[str, Path]:
    manifest = load_json(manifest_path)
    validate_manifest(manifest)
    manifest_dir = manifest_path.parent.resolve()
    output_dir = resolve_path(manifest_dir, manifest["output_dir"])
    if output_dir is None:
        raise ValueError("Manifest output_dir resolved to None.")
    output_dir.mkdir(parents=True, exist_ok=True)

    zotero_cfg = manifest.get("zotero", {})
    zotero_data_dir = resolve_path(manifest_dir, zotero_cfg.get("data_dir")) or DEFAULT_ZOTERO_DATA_DIR
    zotero_exe = resolve_path(manifest_dir, zotero_cfg.get("exe_path")) or DEFAULT_ZOTERO_EXE
    local_user_key = zotero_cfg.get("local_user_key") or DEFAULT_LOCAL_USER_KEY
    allow_title_match_reuse = bool(manifest.get("allow_title_match_reuse", False))

    refs = [
        fetch_crossref_metadata(ReferenceSeed(ref["cite_key"], ref["doi"], ref.get("forced_year")))
        for ref in manifest["references"]
    ]
    write_json(output_dir / "verified_refs.json", refs)
    write_ris(refs, output_dir / "verified_refs.ris")

    stop_zotero()
    backup_dir = backup_zotero_db(output_dir, zotero_data_dir)
    try:
        import_result = import_to_zotero(
            refs,
            manifest["collection_name"],
            zotero_data_dir,
            local_user_key,
            allow_title_match_reuse,
        )
        write_json(
            output_dir / "zotero_import_result.json",
            {"backup_dir": str(backup_dir), "verified_count": len(refs), **import_result},
        )
        output_docx = resolve_path(manifest_dir, manifest["output_docx"])
        if output_docx is None:
            raise ValueError("Manifest output_docx resolved to None.")
        render_document(manifest, import_result, output_docx)
        desktop_copy = resolve_path(manifest_dir, manifest.get("desktop_copy_path"))
        if desktop_copy:
            desktop_copy.parent.mkdir(parents=True, exist_ok=True)
            import shutil

            shutil.copy2(output_docx, desktop_copy)
    except Exception:
        restore_zotero_db(backup_dir, zotero_data_dir)
        raise
    finally:
        start_zotero(zotero_exe)

    return {
        "verified_json": output_dir / "verified_refs.json",
        "verified_ris": output_dir / "verified_refs.ris",
        "import_result": output_dir / "zotero_import_result.json",
        "output_docx": output_docx,
        "desktop_copy": desktop_copy if desktop_copy else output_docx,
    }


def build_manifest_command(args: argparse.Namespace) -> int:
    output_manifest = Path(args.output_manifest).expanduser().resolve()
    manifest = build_manifest_from_files(
        text_path=Path(args.text),
        references_path=Path(args.references),
        collection_name=args.collection_name,
        output_manifest_path=output_manifest,
        output_dir=args.output_dir,
        output_docx=args.output_docx,
        desktop_copy_path=args.desktop_copy_path,
    )
    write_json(output_manifest, manifest)
    print(output_manifest)
    return 0


def from_text_command(args: argparse.Namespace) -> int:
    output_manifest = Path(args.output_manifest).expanduser().resolve()
    manifest = build_manifest_from_files(
        text_path=Path(args.text),
        references_path=Path(args.references),
        collection_name=args.collection_name,
        output_manifest_path=output_manifest,
        output_dir=args.output_dir,
        output_docx=args.output_docx,
        desktop_copy_path=args.desktop_copy_path,
    )
    write_json(output_manifest, manifest)
    outputs = run_from_manifest(output_manifest)
    print(f"manifest={output_manifest}")
    for key, value in outputs.items():
        print(f"{key}={value}")
    return 0


def run_command(args: argparse.Namespace) -> int:
    outputs = run_from_manifest(Path(args.manifest).resolve())
    for key, value in outputs.items():
        print(f"{key}={value}")
    return 0


def add_text_build_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--text", required=True)
    parser.add_argument("--references", required=True)
    parser.add_argument("--collection-name", required=True)
    parser.add_argument("--output-manifest", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--output-docx", required=True)
    parser.add_argument("--desktop-copy-path")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Zotero Word citation automation.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_manifest_parser = subparsers.add_parser("build-manifest", help="Build a manifest from prose and references.")
    add_text_build_arguments(build_manifest_parser)
    build_manifest_parser.set_defaults(func=build_manifest_command)

    from_text_parser = subparsers.add_parser(
        "from-text",
        help="Build a manifest from prose and references, then immediately run the Zotero workflow.",
    )
    add_text_build_arguments(from_text_parser)
    from_text_parser.set_defaults(func=from_text_command)

    run_parser = subparsers.add_parser("run", help="Verify references, import to Zotero, and generate a docx.")
    run_parser.add_argument("--manifest", required=True)
    run_parser.set_defaults(func=run_command)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
