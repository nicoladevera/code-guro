# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0] - 2026-02-07

### Added
- **Interactive Setup Wizard**: Provider selection menu with descriptions and pricing
  - Secure API key input with masking during entry
  - Immediate validation with friendly error messages
  - Secure storage in `~/.config/code-guro/config.json` with 0o600 permissions
  - Config schema v2 with `api_keys` and `preferences` sections
  - Backward compatibility with environment variable fallback
- **Smart Defaults**: Zero-argument `code-guro` command for current directory analysis
  - Auto-detects and previews current project
  - Dry-run mode for fast cost estimation without full file reads
  - Welcome flow for first-time users
  - Edge case handling: home directory warnings, empty directories, recent analysis detection
- **Improved Console Output**: Milestone-based progress tracking with optional emojis
  - Progress indicators with emojis (📊, ✓, ⏳, 📄, 🌐) and `--no-emoji` flag
  - Time estimates based on token count for operations
  - Organized document summaries with clear next steps
  - Progress callbacks in analyzer and generator for real-time updates
- **Emoji Preference Storage**: User preference for emoji display persisted in config
- **Warning Suppression**: Filtered noisy dependency warnings for cleaner user experience
  - Suppresses FutureWarning from Google libraries and urllib3
  - Suppresses OpenSSL-related warnings
  - Only hides warnings users cannot act on

### Changed
- **Setup Flow**: `code-guro configure` success message now recommends simpler `code-guro` command
- **API Key Retrieval**: All providers now check config file before environment variables
- **Config Management**: Enhanced with per-provider API key storage and user preferences

### Fixed
- **API Key Reconfiguration Bug**: Fixed issue where declining to use existing API key would still validate the old key instead of prompting for a new one

### Documentation
- Added comprehensive Phase 1 UX improvements section to AGENTS.md
- Updated README.md Quick Start guide for new interactive setup flow
- Updated UX improvement roadmap with Phase 1 completion and Phase 2 focus

## [0.4.2] - 2025-12-31

### Added
- **Logo branding in HTML output**: Added Code Guro logo to sidebar navigation
  - Logo automatically switches between light and dark versions based on system theme
  - Base64 embedded for self-contained HTML files (no external dependencies)
  - Optimized assets stored in `assets/` directory

### Fixed
- **Mermaid diagram syntax error**: Fixed flowchart diagrams failing to render with "Syntax error" in Mermaid v11.12.2
  - Removed question marks from decision node text (changed `{Binary or Level?}` to `{Binary or Level}`)
  - Removed parentheses from function call labels in node text (changed `[getData()]` to `[getData]`)
  - Added comprehensive Mermaid syntax guidelines to AGENTS.md to prevent future issues
  - Updated prompt templates with inline reminders about Mermaid best practices

## [0.4.1] - 2025-12-30

### Fixed
- **Version string mismatch**: Fixed `code-guro --version` displaying incorrect version (0.3.1 instead of 0.4.x)
  - Updated `__version__` in `src/code_guro/__init__.py` to match package version
  - This was a packaging oversight in v0.4.0 where the version string in the source code wasn't updated

## [0.4.0] - 2025-12-30

### Changed
- **HTML UI Redesign**: Completely redesigned navigation and improved dark mode support
  - Replaced top horizontal navigation bar with modern left sidebar navigation
  - Sidebar navigation: Always visible on desktop (280px fixed width), collapsible hamburger menu on mobile
  - Improved responsive behavior: Sidebar slides in from left on mobile with dark overlay backdrop
  - Consistent spacing between sidebar and main content across all viewport sizes
  - Single close button UX: Hamburger icon hidden when sidebar is open on mobile

### Fixed
- **Mermaid diagram dark mode text readability**: Light-colored diagram boxes (orange, purple, teal) now display dark text in dark mode instead of white text
  - Implemented automatic text color detection based on background luminance
  - Ensures WCAG AA contrast compliance (4.5:1 minimum) for all diagram nodes
  - Works dynamically for any Mermaid diagram colors, not just specific predefined colors
  - Text colors update automatically when system theme changes

### Added
- Accessibility improvements to sidebar navigation:
  - ARIA labels for hamburger menu, close button, and overlay
  - Keyboard-accessible navigation controls
  - Focus indicators for all interactive elements
  - CSS-only hamburger toggle (no JavaScript required for core functionality)

## [0.3.1] - 2025-12-30

### Fixed
- **Section 04 (Module Deep Dives) now generated for large codebases**: Previously, chunked analysis skipped section 04 entirely. Now generates deep dive documents for major modules even when using chunked analysis.
- **Internal analysis files excluded from HTML output**: Files like `_analysis-notes.md` and `_chunk-XX-analysis.md` are now kept in the markdown folder for debugging but excluded from user-facing HTML navigation, resulting in cleaner output for large codebases.

## [0.3.0] - 2025-12-30

### Changed
- **HTML Redesign**: Complete visual overhaul of HTML output with modern, premium aesthetic
  - New card-based layout with soft shadows and rounded corners
  - Soft lavender-gray page background with white content cards
  - Fraunces serif font for headings, Inter sans-serif for body text
  - JetBrains Mono for code blocks
  - Teal accent color for interactive elements and list markers
  - Comprehensive light/dark theme support via CSS variables
  - Sticky navigation bar with pill-shaped links

### Added
- Accessibility improvements for HTML output:
  - Skip link for keyboard navigation
  - ARIA labels and semantic roles
  - Focus-visible indicators for keyboard users
  - Reduced motion support (`prefers-reduced-motion`)
  - Print styles for clean document printing
- Responsive design optimized for mobile, tablet, and desktop viewports
- Mermaid diagram theme now syncs with page theme (light/dark)

## [0.2.0] - 2025-12-29

### Added
- Chunked analysis for large codebases (>150K tokens)
- `code-guro convert` command for adding HTML to markdown-only output
- Dual-format output by default (HTML + markdown in organized subdirectories)
- `--markdown-only` flag for analyze command to generate only markdown
- Pre-commit hooks configuration (`.pre-commit-config.yaml`) for automatic code formatting
- Makefile with convenient commands (`make quality`, `make format`, `make lint`, `make test`)
- Pre-commit as development dependency for automated quality checks
- Comprehensive test suite for dual-format output feature (51 new tests, 84% coverage)
- Test infrastructure with shared fixtures and mocked API calls for fast, offline testing

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

[Unreleased]: https://github.com/nicoladevera/code-guro/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/nicoladevera/code-guro/compare/v0.4.2...v0.5.0
[0.4.2]: https://github.com/nicoladevera/code-guro/compare/v0.4.1...v0.4.2
[0.4.1]: https://github.com/nicoladevera/code-guro/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/nicoladevera/code-guro/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/nicoladevera/code-guro/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/nicoladevera/code-guro/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/nicoladevera/code-guro/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/nicoladevera/code-guro/releases/tag/v0.1.0
