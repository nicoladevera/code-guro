# Sample Outputs

This directory contains sample Markdown and HTML outputs for a fictional app called **"Your Amazing App"**.

## Purpose

These samples serve as reference files for:
- Developers modifying Markdown/HTML generation code
- AI agents working on `html_converter.py`, `generator.py`, or prompt templates
- Testing and validating output formatting changes

## Directory Structure

```
samples/
├── README.md           # This file (committed to git)
├── markdown/           # Sample markdown outputs (git-ignored)
│   ├── 00-overview.md
│   ├── 01-getting-oriented.md
│   ├── 02-architecture.md
│   ├── 03-core-files.md
│   ├── 04-deep-dive-api.md
│   ├── 05-quality-analysis.md
│   └── 06-next-steps.md
└── html/               # Sample HTML outputs (git-ignored)
    └── (matching HTML files)
```

## Features Demonstrated

The sample files showcase all output features:
- Tables (tech stack, file structure, API endpoints)
- Mermaid diagrams (architecture, sequence, flowcharts)
- Code snippets with syntax highlighting
- Glossary definitions
- Risk assessments and quality metrics

## Regenerating Samples

To regenerate HTML from the markdown samples:

```bash
make samples
```

This runs the HTML converter on `samples/markdown/` and outputs to `samples/html/`.

## Note

The `markdown/` and `html/` directories are git-ignored. Only this README is committed to the repository. Each developer/agent maintains their own local copy of the sample outputs.
