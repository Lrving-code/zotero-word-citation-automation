# Contributing

## Scope

This project targets a Windows-first workflow that integrates:

- Crossref DOI verification
- local Zotero desktop storage
- Microsoft Word `.docx` citation field generation

## Development setup

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .[dev]
```

## Before opening a pull request

```powershell
python -m pytest
python -m py_compile src\zotero_wordflow\*.py
```

## Contribution guidelines

- Keep platform-specific assumptions isolated in `windows_paths.py`
- Do not commit local Zotero databases, backups, or generated `.docx` outputs
- Prefer explicit failure over silent fallback when citation matching is ambiguous
- Update docs when CLI behavior changes
