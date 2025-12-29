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

3. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

4. Run tests:
   ```bash
   pytest
   ```

## Code Style

- Format code with Black: `black src/`
- Lint with Ruff: `ruff check src/`
- Run both before committing

## Making Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and add tests

3. Ensure tests pass:
   ```bash
   pytest
   ```

4. Commit with a descriptive message

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
