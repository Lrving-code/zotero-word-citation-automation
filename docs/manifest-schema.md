# Manifest schema

The runner consumes a JSON manifest with these top-level fields:

```json
{
  "collection_name": "target zotero collection",
  "output_dir": "directory for verification and import outputs",
  "output_docx": "final docx path",
  "desktop_copy_path": "optional convenience copy path",
  "zotero": {
    "data_dir": "optional Zotero data directory override",
    "exe_path": "optional Zotero executable override",
    "local_user_key": "optional local library user key override"
  },
  "allow_title_match_reuse": false,
  "references": [
    {
      "cite_key": "ShortKey2024",
      "doi": "10.xxxx/xxxx",
      "forced_year": 2024
    }
  ],
  "document": {
    "title": "Document title",
    "elements": []
  }
}
```

Relative paths are resolved relative to the manifest file location.

## Supported element types

### Heading

```json
{
  "type": "heading",
  "level": 1,
  "text": "2.1 Section Title"
}
```

Special case:

```json
{
  "type": "heading",
  "level": "title",
  "text": "Main Title"
}
```

### Paragraph

```json
{
  "type": "paragraph",
  "segments": [
    { "text": "Plain text before a citation" },
    {
      "citations": [
        { "cite_key": "Smith2020", "display_text": "Smith et al., 2020" },
        { "cite_key": "Jones2021", "display_text": "Jones & Li, 2021" }
      ]
    },
    { "text": "Plain text after the citation." }
  ]
}
```

## Helper limitations

- parenthetical author-year citations are supported
- ambiguous author-year collisions stop the helper with an error
- narrative citations such as `Smith (2020)` are not automatically converted yet
