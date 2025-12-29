"""Tests for config module."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from code_guro.config import (
    get_api_key,
    get_config_dir,
    get_config_file,
    is_api_key_configured,
    mask_api_key,
    read_config,
    save_api_key,
    write_config,
)


class TestConfigDir:
    """Tests for config directory functions."""

    def test_get_config_dir_returns_path(self):
        """Config dir should return a Path object."""
        result = get_config_dir()
        assert isinstance(result, Path)

    def test_get_config_dir_ends_with_code_guro(self):
        """Config dir should end with 'code-guro'."""
        result = get_config_dir()
        assert result.name == "code-guro"

    def test_get_config_file_returns_json(self):
        """Config file should be config.json."""
        result = get_config_file()
        assert result.name == "config.json"


class TestReadWriteConfig:
    """Tests for reading and writing config."""

    def test_read_config_empty_when_no_file(self):
        """Should return empty dict when no config file exists."""
        with patch("code_guro.config.get_config_file") as mock_file:
            mock_file.return_value = Path("/nonexistent/config.json")
            result = read_config()
            assert result == {}

    def test_write_and_read_config(self):
        """Should be able to write and read config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"

            with patch("code_guro.config.get_config_file") as mock_file:
                with patch("code_guro.config.ensure_config_dir") as mock_dir:
                    mock_file.return_value = config_path
                    mock_dir.return_value = Path(tmpdir)

                    test_config = {"api_key": "test-key-123"}
                    write_config(test_config)

                    result = read_config()
                    assert result == test_config


class TestApiKey:
    """Tests for API key functions."""

    def test_get_api_key_from_env(self):
        """Should get API key from environment variable."""
        with patch.dict(os.environ, {"CLAUDE_API_KEY": "env-key-123"}):
            result = get_api_key()
            assert result == "env-key-123"

    def test_get_api_key_anthropic_env(self):
        """Should get API key from ANTHROPIC_API_KEY env var."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "anthropic-key-123"}, clear=True):
            with patch("code_guro.config.read_config", return_value={}):
                # Clear CLAUDE_API_KEY if it exists
                env = os.environ.copy()
                env.pop("CLAUDE_API_KEY", None)
                with patch.dict(os.environ, env, clear=True):
                    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "anthropic-key-123"}):
                        result = get_api_key()
                        assert result == "anthropic-key-123"

    def test_get_api_key_from_config(self):
        """Should get API key from config file when not in env."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("code_guro.config.read_config", return_value={"api_key": "config-key-123"}):
                result = get_api_key()
                assert result == "config-key-123"

    def test_is_api_key_configured_true(self):
        """Should return True when API key is configured."""
        with patch("code_guro.config.get_api_key", return_value="some-key"):
            assert is_api_key_configured() is True

    def test_is_api_key_configured_false(self):
        """Should return False when API key is not configured."""
        with patch("code_guro.config.get_api_key", return_value=None):
            assert is_api_key_configured() is False


class TestMaskApiKey:
    """Tests for API key masking."""

    def test_mask_api_key_normal(self):
        """Should mask middle of key."""
        result = mask_api_key("sk-ant-api-key-12345")
        assert result == "sk-ant-...2345"

    def test_mask_api_key_short(self):
        """Should return **** for short keys."""
        result = mask_api_key("short")
        assert result == "****"

    def test_mask_api_key_empty(self):
        """Should return **** for empty keys."""
        result = mask_api_key("")
        assert result == "****"

    def test_mask_api_key_none(self):
        """Should return **** for None."""
        result = mask_api_key(None)
        assert result == "****"
