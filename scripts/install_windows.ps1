python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
Write-Host "Installed zotero-wordflow into .venv"
