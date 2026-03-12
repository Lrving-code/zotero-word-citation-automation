# Architecture

Core flow:

1. `prose_manifest.py`
   - turns prose and references into a manifest
2. `manifest.py`
   - validates structure and resolves manifest-relative paths
3. `doi_verify.py`
   - verifies DOI-backed references via Crossref
4. `zotero_import.py`
   - stops Zotero, backs up the database, imports references, and restores on failure
5. `docx_fields.py`
   - writes Zotero-compatible citation fields into `.docx`
6. `cli.py`
   - exposes `build-manifest` and `run`

Design choice:

- prefer explicit failure over silent fallback
- keep Windows-specific assumptions isolated
- treat Codex skill integration as optional, not as the core product
