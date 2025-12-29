# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Chunked analysis for large codebases (>150K tokens)
- `code-guro convert` command for adding HTML to markdown-only output
- Dual-format output by default (HTML + markdown in organized subdirectories)
- `--markdown-only` flag for analyze command to generate only markdown

### Changed
- **Breaking**: `code-guro analyze` now generates both HTML and markdown by default, organized in `html/` and `markdown/` subdirectories
- **Breaking**: Removed `--format` flag, replaced with `--markdown-only` for simpler UX
- Output directory structure now cleaner with format-specific subdirectories
- HTML output is now the recommended format for best diagram rendering experience

## [0.1.0] - 2025-12-28

### Added
- Initial release
- `code-guro analyze` command for generating codebase documentation
- `code-guro explain` command for deep-diving into specific files/folders
- `code-guro configure` command for API key setup
- Framework detection for Next.js, React, Vue, Django, Flask, Express, Rails
- Markdown and HTML output formats
- Mermaid diagram generation for architecture visualization
- Interactive REPL mode for Q&A sessions
- Cost estimation with confirmation for large codebases
- Secure API key storage in `~/.config/code-guro/`

[Unreleased]: https://github.com/nicoladevera/code-guro/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/nicoladevera/code-guro/releases/tag/v0.1.0
