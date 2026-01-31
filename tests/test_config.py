"""Tests for configuration loading."""

import os
import tempfile
from pathlib import Path

import pytest

from paper2skill.utils.config import (
    load_config,
    get_model_config,
    _merge_config,
    _apply_env_overrides,
    DEFAULT_CONFIG,
)


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_default_config(self):
        """Test loading default configuration when no file exists."""
        # Use a path that doesn't exist
        config = load_config("/nonexistent/path/config.yaml")
        
        assert "default_model" in config
        assert "models" in config
        assert "openai" in config["models"]

    def test_load_config_from_file(self, tmp_path):
        """Test loading configuration from a YAML file."""
        config_content = """
default_model: anthropic
models:
  anthropic:
    provider: anthropic
    model_name: claude-3-sonnet
    temperature: 0.5
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        config = load_config(str(config_file))
        
        assert config["default_model"] == "anthropic"
        assert "anthropic" in config["models"]
        assert config["models"]["anthropic"]["model_name"] == "claude-3-sonnet"
        assert config["models"]["anthropic"]["temperature"] == 0.5

    def test_load_config_merges_with_defaults(self, tmp_path):
        """Test that file config merges with defaults."""
        config_content = """
default_model: custom
models:
  custom:
    provider: openai
    model_name: gpt-4
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        config = load_config(str(config_file))
        
        # Check custom config is loaded
        assert config["default_model"] == "custom"
        assert "custom" in config["models"]
        
        # Check default openai is still present
        assert "openai" in config["models"]


class TestMergeConfig:
    """Tests for _merge_config function."""

    def test_merge_simple_values(self):
        """Test merging simple key-value pairs."""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        
        result = _merge_config(base, override)
        
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_merge_nested_dicts(self):
        """Test merging nested dictionaries."""
        base = {
            "models": {
                "openai": {"model_name": "gpt-3.5", "temperature": 0}
            }
        }
        override = {
            "models": {
                "openai": {"temperature": 0.5},
                "anthropic": {"model_name": "claude"}
            }
        }
        
        result = _merge_config(base, override)
        
        assert result["models"]["openai"]["model_name"] == "gpt-3.5"
        assert result["models"]["openai"]["temperature"] == 0.5
        assert result["models"]["anthropic"]["model_name"] == "claude"


class TestApplyEnvOverrides:
    """Tests for _apply_env_overrides function."""

    def test_override_api_key_from_env(self, monkeypatch):
        """Test that API keys can be set from environment variables."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
        
        config = {"models": {"openai": {"provider": "openai"}}}
        result = _apply_env_overrides(config)
        
        assert result["models"]["openai"]["api_key"] == "test-key-123"

    def test_override_default_model_from_env(self, monkeypatch):
        """Test that default_model can be overridden via environment variable."""
        monkeypatch.setenv("PAPER2SKILL_MODEL", "anthropic")
        
        config = {"default_model": "openai", "models": {}}
        result = _apply_env_overrides(config)
        
        assert result["default_model"] == "anthropic"

    def test_multiple_api_keys_from_env(self, monkeypatch):
        """Test that multiple API keys can be set from environment."""
        monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-key")
        
        config = {
            "models": {
                "openai": {"provider": "openai"},
                "anthropic": {"provider": "anthropic"}
            }
        }
        result = _apply_env_overrides(config)
        
        assert result["models"]["openai"]["api_key"] == "openai-key"
        assert result["models"]["anthropic"]["api_key"] == "anthropic-key"

    def test_api_key_applied_to_custom_model_by_provider(self, monkeypatch):
        """Test that API keys are applied to custom models based on provider."""
        monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
        
        config = {
            "models": {
                "my-custom-gpt4": {"provider": "openai", "model_name": "gpt-4"}
            }
        }
        result = _apply_env_overrides(config)
        
        assert result["models"]["my-custom-gpt4"]["api_key"] == "openai-key"

    def test_existing_api_key_not_overwritten_by_env(self, monkeypatch):
        """Test that existing api_key in config is not overwritten by environment variable."""
        monkeypatch.setenv("OPENAI_API_KEY", "env-key")
        
        config = {
            "models": {
                "openai": {"provider": "openai", "api_key": "config-key"}
            }
        }
        result = _apply_env_overrides(config)
        
        # The existing api_key should NOT be overwritten
        assert result["models"]["openai"]["api_key"] == "config-key"


class TestGetModelConfig:
    """Tests for get_model_config function."""

    def test_get_default_model(self):
        """Test getting the default model configuration."""
        config = {
            "default_model": "openai",
            "models": {
                "openai": {"provider": "openai", "model_name": "gpt-3.5-turbo"}
            }
        }
        
        result = get_model_config(config)
        
        assert result["provider"] == "openai"
        assert result["model_name"] == "gpt-3.5-turbo"

    def test_get_specific_model(self):
        """Test getting a specific model configuration."""
        config = {
            "default_model": "openai",
            "models": {
                "openai": {"provider": "openai", "model_name": "gpt-3.5-turbo"},
                "anthropic": {"provider": "anthropic", "model_name": "claude-3"}
            }
        }
        
        result = get_model_config(config, "anthropic")
        
        assert result["provider"] == "anthropic"
        assert result["model_name"] == "claude-3"

    def test_model_not_found_raises_error(self):
        """Test that requesting a non-existent model raises ValueError."""
        config = {
            "default_model": "openai",
            "models": {"openai": {"provider": "openai"}}
        }
        
        with pytest.raises(ValueError) as exc_info:
            get_model_config(config, "nonexistent")
        
        assert "nonexistent" in str(exc_info.value)
        assert "not found" in str(exc_info.value)


class TestIntegration:
    """Integration tests for configuration loading."""

    def test_full_config_flow(self, tmp_path, monkeypatch):
        """Test the full configuration loading flow."""
        # Create a config file
        config_content = """
default_model: openai-gpt4
models:
  openai-gpt4:
    provider: openai
    model_name: gpt-4
    temperature: 0.1
  anthropic:
    provider: anthropic
    model_name: claude-3-sonnet
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        # Set an API key via environment
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        
        # Load config
        config = load_config(str(config_file))
        
        # Get model config
        model_config = get_model_config(config)
        
        # Verify
        assert model_config["provider"] == "openai"
        assert model_config["model_name"] == "gpt-4"
        assert model_config["temperature"] == 0.1
        assert model_config["api_key"] == "test-key"
