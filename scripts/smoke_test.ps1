python -m pytest
python -m zotero_wordflow build-manifest `
  --text examples\sample_prose.txt `
  --references examples\sample_references.txt `
  --collection-name "demo refs" `
  --output-manifest outputs\manifest.json `
  --output-dir outputs\run `
  --output-docx outputs\run\sample.docx
Write-Host "Smoke test finished. Use the generated manifest only on a machine with Zotero and Word."
