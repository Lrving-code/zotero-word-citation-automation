# Security Policy

## Do not commit

- local Zotero profile contents
- `zotero.sqlite`, `zotero.sqlite-wal`, `zotero.sqlite-shm`
- Word temporary files such as `~$*.docx`
- exported user documents containing private content
- API tokens or GitHub credentials

## Risk notes

This project writes to a local Zotero database by design. Always test with a backed-up profile first if you are adapting the workflow to a new environment.

## Reporting

If you find a security issue, avoid posting secrets or private documents in a public issue. Open a minimal report describing impact and reproduction conditions.
