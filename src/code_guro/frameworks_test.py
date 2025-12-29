"""Tests for frameworks module."""

import json
import tempfile
from pathlib import Path

import pytest

from code_guro.frameworks import (
    FRAMEWORK_METADATA,
    detect_django,
    detect_express,
    detect_flask,
    detect_frameworks,
    detect_nextjs,
    detect_rails,
    detect_react,
    detect_vue,
    get_framework_context,
)


class TestFrameworkMetadata:
    """Tests for framework metadata."""

    def test_metadata_has_required_frameworks(self):
        """Should have metadata for all MVP frameworks."""
        assert "nextjs" in FRAMEWORK_METADATA
        assert "react" in FRAMEWORK_METADATA
        assert "vue" in FRAMEWORK_METADATA
        assert "django" in FRAMEWORK_METADATA
        assert "flask" in FRAMEWORK_METADATA
        assert "express" in FRAMEWORK_METADATA
        assert "rails" in FRAMEWORK_METADATA

    def test_metadata_has_required_fields(self):
        """Each framework should have required fields."""
        for key, info in FRAMEWORK_METADATA.items():
            assert info.name, f"{key} missing name"
            assert info.description, f"{key} missing description"
            assert info.architecture, f"{key} missing architecture"
            assert len(info.conventions) > 0, f"{key} missing conventions"
            assert len(info.gotchas) > 0, f"{key} missing gotchas"


class TestNextJsDetection:
    """Tests for Next.js detection."""

    def test_detect_nextjs_with_package_json(self):
        """Should detect Next.js from package.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            package_json = Path(tmpdir) / "package.json"
            package_json.write_text(json.dumps({
                "dependencies": {"next": "^14.0.0", "react": "^18.0.0"}
            }))

            result = detect_nextjs(Path(tmpdir))
            assert result is not None
            assert result.name == "Next.js"

    def test_detect_nextjs_no_package_json(self):
        """Should return None when no package.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = detect_nextjs(Path(tmpdir))
            assert result is None


class TestReactDetection:
    """Tests for React detection."""

    def test_detect_react_from_package_json(self):
        """Should detect React from package.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            package_json = Path(tmpdir) / "package.json"
            package_json.write_text(json.dumps({
                "dependencies": {"react": "^18.0.0"}
            }))

            result = detect_react(Path(tmpdir))
            assert result is not None
            assert result.name == "React"


class TestVueDetection:
    """Tests for Vue detection."""

    def test_detect_vue_from_package_json(self):
        """Should detect Vue from package.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            package_json = Path(tmpdir) / "package.json"
            package_json.write_text(json.dumps({
                "dependencies": {"vue": "^3.0.0"}
            }))

            result = detect_vue(Path(tmpdir))
            assert result is not None
            assert result.name == "Vue.js"


class TestDjangoDetection:
    """Tests for Django detection."""

    def test_detect_django_with_manage_py(self):
        """Should detect Django with manage.py and requirements.txt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manage_py = Path(tmpdir) / "manage.py"
            manage_py.write_text("#!/usr/bin/env python")

            requirements = Path(tmpdir) / "requirements.txt"
            requirements.write_text("Django>=4.0\n")

            result = detect_django(Path(tmpdir))
            assert result is not None
            assert result.name == "Django"

    def test_detect_django_no_manage_py(self):
        """Should return None without manage.py."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = detect_django(Path(tmpdir))
            assert result is None


class TestFlaskDetection:
    """Tests for Flask detection."""

    def test_detect_flask_from_requirements(self):
        """Should detect Flask from requirements.txt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            requirements = Path(tmpdir) / "requirements.txt"
            requirements.write_text("Flask>=2.0\n")

            result = detect_flask(Path(tmpdir))
            assert result is not None
            assert result.name == "Flask"

    def test_detect_flask_from_app_py(self):
        """Should detect Flask from app.py imports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app_py = Path(tmpdir) / "app.py"
            app_py.write_text("from flask import Flask\napp = Flask(__name__)")

            result = detect_flask(Path(tmpdir))
            assert result is not None
            assert result.name == "Flask"


class TestExpressDetection:
    """Tests for Express detection."""

    def test_detect_express_from_package_json(self):
        """Should detect Express from package.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            package_json = Path(tmpdir) / "package.json"
            package_json.write_text(json.dumps({
                "dependencies": {"express": "^4.18.0"}
            }))

            result = detect_express(Path(tmpdir))
            assert result is not None
            assert result.name == "Express.js"


class TestRailsDetection:
    """Tests for Rails detection."""

    def test_detect_rails_with_gemfile_and_routes(self):
        """Should detect Rails with Gemfile and routes.rb."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gemfile = Path(tmpdir) / "Gemfile"
            gemfile.write_text("gem 'rails', '~> 7.0'\n")

            config_dir = Path(tmpdir) / "config"
            config_dir.mkdir()
            routes = config_dir / "routes.rb"
            routes.write_text("Rails.application.routes.draw do\nend")

            result = detect_rails(Path(tmpdir))
            assert result is not None
            assert result.name == "Ruby on Rails"


class TestDetectFrameworks:
    """Tests for framework detection aggregation."""

    def test_detect_multiple_frameworks(self):
        """Should detect multiple frameworks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            package_json = Path(tmpdir) / "package.json"
            package_json.write_text(json.dumps({
                "dependencies": {
                    "next": "^14.0.0",
                    "react": "^18.0.0"
                }
            }))

            result = detect_frameworks(Path(tmpdir))
            names = [f.name for f in result]

            assert "Next.js" in names
            assert "React" in names

    def test_detect_no_frameworks(self):
        """Should return empty list when no frameworks detected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = detect_frameworks(Path(tmpdir))
            assert result == []


class TestGetFrameworkContext:
    """Tests for framework context generation."""

    def test_get_framework_context_empty(self):
        """Should return empty string for no frameworks."""
        result = get_framework_context([])
        assert result == ""

    def test_get_framework_context_includes_name(self):
        """Should include framework name in context."""
        frameworks = [FRAMEWORK_METADATA["react"]]
        result = get_framework_context(frameworks)
        assert "React" in result

    def test_get_framework_context_includes_sections(self):
        """Should include architecture and conventions."""
        frameworks = [FRAMEWORK_METADATA["django"]]
        result = get_framework_context(frameworks)
        assert "Architecture" in result
        assert "Conventions" in result
        assert "Gotchas" in result
