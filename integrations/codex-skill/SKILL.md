---
name: zotero-wordflow
description: This skill should be used when the user asks to generate a Word document with Zotero citations, import DOI-verified references into Zotero, or turn prose plus references into a bibliography-ready docx.
version: 0.1.1
---

# zotero-wordflow

Use this skill when the user provides:

- a Zotero collection name,
- prose or a manifest,
- a DOI-backed reference list,
- and wants a Word document with Zotero-compatible citation fields.

## Prerequisite

Install the Python package first in an environment available to the current Python interpreter:

```powershell
python -m pip install zotero-wordflow
```

For local development, install from the cloned repository:

```powershell
python -m pip install -e .
```

## Workflow

1. If the user gives prose and references, prefer:
   - `python -m zotero_wordflow from-text ...`
2. If debugging manifest content is necessary, run:
   - `scripts/build_manifest_from_natural_text.py`
3. Then run:
   - `scripts/run_zotero_wordflow.py`
4. Return the generated `.docx` path and remind the user to run `Refresh` and `Add/Edit Bibliography` inside Word.

## Robustness notes

- UTF-8 BOM input files should be accepted automatically.
- Do not parallelize `build-manifest` and `run`; `run` depends on the manifest file already existing.
- Prefer manifest-relative output paths when the workspace contains non-ASCII folder names on Windows.

## Reference Files

- `references/README.md.txt`
- `references/manifest-schema.md`

## Limits

- Parenthetical author-year citations are supported.
- Narrative citations such as `Smith (2020)` are not automatically converted.
- Ambiguous or unresolved citation groups should fail loudly, not be silently downgraded.
