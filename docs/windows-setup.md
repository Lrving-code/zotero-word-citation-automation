# Windows setup

## Required software

- Python 3.10 or newer
- Zotero Desktop
- Microsoft Word
- Zotero Word add-in

## Recommended checks

1. Open Zotero
2. Open Word
3. Confirm the `Zotero` ribbon tab exists
4. Click `Document Preferences` in a test document
5. If the ribbon does nothing, reinstall the Word add-in from Zotero first

## Default paths

The package assumes these defaults unless overridden in the manifest:

- Zotero data dir: `%USERPROFILE%\\Zotero`
- Zotero executable: `%ProgramFiles%\\Zotero\\zotero.exe`
- local library user key: `ZOTERO_LOCAL_USER_KEY` env var if set
