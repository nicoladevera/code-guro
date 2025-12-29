# Contributing to Code Guro

Thank you for your interest in contributing to Code Guro!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/nicoladevera/code-guro.git
   cd code-guro
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode with dev dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Set up pre-commit hooks (recommended):
   ```bash
   pre-commit install
   ```

   This will automatically run Black and Ruff before each commit, preventing formatting issues.

5. Run tests:
   ```bash
   pytest
   ```

## Code Style

We use Black for formatting and Ruff for linting.

### Automatic Checks (Recommended)

If you installed pre-commit hooks (step 4 above), these checks will run automatically before each commit:
- Black formatting
- Ruff linting
- Trailing whitespace removal
- File ending fixes

### Manual Checks

If you prefer to run checks manually:

```bash
# Quick way - using Makefile
make quality

# Or run checks individually:
black src/              # Format code
ruff check src/ --fix   # Lint and auto-fix
pytest                  # Run tests
```

### Other Useful Make Commands

```bash
make help         # Show all available commands
make format       # Format code only
make lint         # Lint code only
make test         # Run tests only
make pre-commit   # Run pre-commit on all files
make clean        # Clean up cache files
```

### Python Version Compatibility

We support Python 3.8+. Keep these guidelines in mind:

- **Type hints**: Use `from __future__ import annotations` at the top of files that use modern type syntax
- **Avoid Python 3.9+ syntax**: Don't use `list[str]` or `dict[str, int]` without the future import; use `List[str]` from `typing` or add the annotations import
- **Avoid Python 3.10+ syntax**: Don't use `str | None`; use `Optional[str]` from `typing` instead

## Making Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and add tests

3. **Quality checks will run automatically** when you commit (if you set up pre-commit hooks)

   Or run manually:
   ```bash
   make quality
   ```

4. Commit with a descriptive message (hooks will auto-format your code)

5. Push and create a Pull Request

## Release Process

Releases are automated via GitHub Actions when a version tag is pushed.

### For Maintainers: How to Release

1. **Update the version** in `src/code_guro/__init__.py`:
   ```python
   __version__ = "0.2.0"  # New version
   ```

2. **Update CHANGELOG.md**:
   - Move items from `[Unreleased]` to a new version section
   - Add the release date
   - Update the comparison links at the bottom

3. **Commit the version bump**:
   ```bash
   git add src/code_guro/__init__.py CHANGELOG.md
   git commit -m "Bump version to 0.2.0"
   git push origin main
   ```

4. **Create and push a tag**:
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

5. **GitHub Actions will automatically**:
   - Build the package
   - Publish to PyPI
   - Create a GitHub Release

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.2.0): New features, backwards compatible
- **PATCH** (0.1.1): Bug fixes, backwards compatible

While in 0.x.x, the API is considered unstable and minor versions may include breaking changes.

## Reporting Issues

- Use GitHub Issues for bug reports and feature requests
- Include your Python version and OS
- For bugs, include steps to reproduce

## Questions?

Feel free to open an issue for any questions about contributing.
