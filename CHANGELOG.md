# Changelog

All notable changes to this project will be documented in this file.

## [0.1.3] - 2026-03-13

### Fixed

- Accepted the `and` form in two-author narrative citations such as `Dark and Bram (2007)`.
- Aligned runtime metadata by updating the Crossref user agent string to `0.1.3`.
- Removed the README roadmap contradiction after narrative citation support shipped.
- Changed the Codex installer so the legacy skill alias is derived from the canonical skill instead of drifting as a separate hard-coded copy.

## [0.1.2] - 2026-03-13

### Fixed

- Rendered one parenthetical citation group as one Zotero field instead of stacking multiple one-item fields inside the same brackets.
- Added helper support for simple narrative citations such as `Smith (2020)`.
- Accepted the `and` form in two-author narrative citations such as `Dark and Bram (2007)`.
- Kept grouped and narrative citation rendering aligned with Zotero field semantics by using multi-item citation payloads and `suppressAuthor` where needed.
- Aligned runtime metadata by updating the Crossref user agent string to `0.1.2`.
- Changed the Codex installer so the legacy skill alias is derived from the canonical skill instead of drifting as a separate hard-coded copy.

### Added

- Added XML-level rendering tests for grouped citations and narrative citation fields.

## [0.1.1] - 2026-03-13

### Fixed

- Accepted UTF-8 with BOM for prose, reference lists, and manifest JSON files.
- Stripped BOM and zero-width characters before author-year citation matching.
- Fixed block-level BOM and zero-width characters so headings are still recognized correctly.
- Fixed the Codex skill installer path resolution so the packaged skill can be installed correctly from the repository.

### Added

- Added `from-text` CLI command to run manifest generation and Zotero import sequentially in one step.
- Added tests covering BOM-tolerant parsing, zero-width character cleanup, block-level heading recovery, and the new CLI flow.

## [0.1.0] - 2026-03-12

### Added

- Initial standalone open-source release of `zotero-wordflow`.
- Manifest-driven Zotero to Word workflow for DOI-backed references.
- Natural-language helper that converts prose plus references into a runnable manifest.
- Windows-first Codex skill integration for cross-thread reuse.
- Test suite covering manifest validation and prose-to-manifest conversion.
- GitHub Actions CI, contribution guides, security policy, and issue templates.
