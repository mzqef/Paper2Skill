"""Configuration management for Paper2Skill."""

import copy
import os
from pathlib import Path
from typing import Any, Dict, Optional

# Default configuration values
DEFAULT_CONFIG = {
    "default_model": "openai",
    "models": {
        "openai": {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo",
            "temperature": 0,
        }
    }
}


def _find_config_file() -> Optional[Path]:
    """
    Find the configuration file in common locations.
    
    Searches in order:
    1. Current working directory
    2. User's home directory
    3. Package directory
    
    Returns:
        Path to config file if found, None otherwise
    """
    config_names = ["config.yaml", "config.yml", "paper2skill.yaml", "paper2skill.yml"]
    
    # Search locations in priority order
    search_paths = [
        Path.cwd(),
        Path.home(),
        Path(__file__).parent.parent.parent,  # Repository root
    ]
    
    for search_path in search_paths:
        for config_name in config_names:
            config_path = search_path / config_name
            if config_path.exists():
                return config_path
    
    return None


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Optional path to config file. If not provided,
                    searches for config file in common locations.
    
    Returns:
        Configuration dictionary with model settings
    """
    config = copy.deepcopy(DEFAULT_CONFIG)
    
    # Find config file
    if config_path:
        path = Path(config_path)
    else:
        path = _find_config_file()
    
    if path and path.exists():
        try:
            import yaml
            with open(path, 'r') as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    # Merge file config with defaults
                    config = _merge_config(config, file_config)
        except ImportError:
            print("Warning: PyYAML not installed. Using default configuration.")
        except Exception as e:
            print(f"Warning: Could not load config from {path}: {e}")
    
    # Override with environment variables if present
    config = _apply_env_overrides(config)
    
    return config


def _merge_config(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two configuration dictionaries.
    
    Args:
        base: Base configuration dictionary
        override: Override configuration dictionary
        
    Returns:
        Merged configuration dictionary
    """
    result = copy.deepcopy(base)
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_config(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    
    return result


def _apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply environment variable overrides to configuration.
    
    Supported environment variables:
    - OPENAI_API_KEY: API key for OpenAI and OpenAI-based models
    - ANTHROPIC_API_KEY: API key for Anthropic
    - AZURE_OPENAI_API_KEY: API key for Azure OpenAI
    - PAPER2SKILL_MODEL: Override default model selection
    
    Args:
        config: Current configuration dictionary
        
    Returns:
        Configuration with environment overrides applied
    """
    # Map providers to their environment variables
    provider_env_vars = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "azure": "AZURE_OPENAI_API_KEY",
    }
    
    # Apply API keys to all models based on their provider
    models = config.get("models", {})
    for model_name, model_config in models.items():
        provider = model_config.get("provider", "")
        env_var = provider_env_vars.get(provider)
        if env_var:
            api_key = os.getenv(env_var)
            if api_key and "api_key" not in model_config:
                model_config["api_key"] = api_key
    
    # Allow overriding default model via environment variable
    default_model = os.getenv("PAPER2SKILL_MODEL")
    if default_model:
        config["default_model"] = default_model
    
    return config


def get_model_config(config: Dict[str, Any], model_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get configuration for a specific model.
    
    Args:
        config: Full configuration dictionary
        model_name: Name of the model to get config for.
                   If None, uses the default_model from config.
    
    Returns:
        Model-specific configuration dictionary
        
    Raises:
        ValueError: If the specified model is not found in configuration
    """
    if model_name is None:
        model_name = config.get("default_model", "openai")
    
    models = config.get("models", {})
    
    if model_name not in models:
        available = list(models.keys())
        raise ValueError(
            f"Model '{model_name}' not found in configuration. "
            f"Available models: {available}"
        )
    
    return models[model_name]
