from __future__ import annotations

import os
from pathlib import Path


DEFAULT_ZOTERO_DATA_DIR = Path.home() / "Zotero"
DEFAULT_ZOTERO_EXE = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Zotero" / "zotero.exe"
DEFAULT_LOCAL_USER_KEY = os.environ.get("ZOTERO_LOCAL_USER_KEY", "p5QmjtW7")
