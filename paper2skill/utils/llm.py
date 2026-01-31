"""Utility functions for Paper2Skill."""

import os
from typing import Any, Dict, Optional

from .config import load_config, get_model_config


def get_llm(model_name: Optional[str] = None, config_path: Optional[str] = None):
    """
    Get a language model instance based on configuration.
    
    Args:
        model_name: Name of the model configuration to use (e.g., "openai", "anthropic").
                   If None, uses the default_model from configuration.
        config_path: Optional path to config file. If not provided,
                    searches for config file in common locations.
        
    Returns:
        Language model instance or None if configuration/API key not available
    """
    # Load configuration
    config = load_config(config_path)
    
    try:
        model_config = get_model_config(config, model_name)
    except ValueError as e:
        print(f"Warning: {e}. Running in fallback mode.")
        return None
    
    provider = model_config.get("provider", "openai")
    
    # Route to appropriate provider
    if provider == "openai":
        return _get_openai_llm(model_config)
    elif provider == "anthropic":
        return _get_anthropic_llm(model_config)
    elif provider == "azure":
        return _get_azure_llm(model_config)
    elif provider == "ollama":
        return _get_ollama_llm(model_config)
    else:
        print(f"Warning: Unknown provider '{provider}'. Running in fallback mode.")
        return None


def _get_openai_llm(config: Dict[str, Any]):
    """
    Get an OpenAI language model instance.
    
    Args:
        config: Model configuration dictionary
        
    Returns:
        ChatOpenAI instance or None if unavailable
    """
    try:
        from langchain_openai import ChatOpenAI
        
        api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Warning: OpenAI API key not found. Running in fallback mode.")
            return None
        
        return ChatOpenAI(
            model=config.get("model_name", "gpt-3.5-turbo"),
            temperature=config.get("temperature", 0),
            api_key=api_key,
        )
    except ImportError:
        print("Warning: langchain_openai not installed. Running in fallback mode.")
        return None
    except Exception as e:
        print(f"Warning: Could not initialize OpenAI LLM: {e}. Running in fallback mode.")
        return None


def _get_anthropic_llm(config: Dict[str, Any]):
    """
    Get an Anthropic language model instance.
    
    Args:
        config: Model configuration dictionary
        
    Returns:
        ChatAnthropic instance or None if unavailable
    """
    try:
        from langchain_anthropic import ChatAnthropic
        
        api_key = config.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("Warning: Anthropic API key not found. Running in fallback mode.")
            return None
        
        return ChatAnthropic(
            model=config.get("model_name", "claude-3-sonnet-20240229"),
            temperature=config.get("temperature", 0),
            api_key=api_key,
        )
    except ImportError:
        print("Warning: langchain_anthropic not installed. Running in fallback mode.")
        return None
    except Exception as e:
        print(f"Warning: Could not initialize Anthropic LLM: {e}. Running in fallback mode.")
        return None


def _get_azure_llm(config: Dict[str, Any]):
    """
    Get an Azure OpenAI language model instance.
    
    Args:
        config: Model configuration dictionary
        
    Returns:
        AzureChatOpenAI instance or None if unavailable
    """
    try:
        from langchain_openai import AzureChatOpenAI
        
        api_key = config.get("api_key") or os.getenv("AZURE_OPENAI_API_KEY")
        if not api_key:
            print("Warning: Azure OpenAI API key not found. Running in fallback mode.")
            return None
        
        azure_endpoint = config.get("azure_endpoint")
        if not azure_endpoint:
            print("Warning: Azure endpoint not configured. Running in fallback mode.")
            return None
        
        return AzureChatOpenAI(
            deployment_name=config.get("deployment_name", "gpt-35-turbo"),
            api_version=config.get("api_version", "2024-02-15-preview"),
            azure_endpoint=azure_endpoint,
            temperature=config.get("temperature", 0),
            api_key=api_key,
        )
    except ImportError:
        print("Warning: langchain_openai not installed. Running in fallback mode.")
        return None
    except Exception as e:
        print(f"Warning: Could not initialize Azure OpenAI LLM: {e}. Running in fallback mode.")
        return None


def _get_ollama_llm(config: Dict[str, Any]):
    """
    Get an Ollama (local) language model instance.
    
    Args:
        config: Model configuration dictionary
        
    Returns:
        ChatOllama instance or None if unavailable
    """
    try:
        from langchain_ollama import ChatOllama
        
        return ChatOllama(
            model=config.get("model_name", "llama2"),
            base_url=config.get("base_url", "http://localhost:11434"),
            temperature=config.get("temperature", 0),
        )
    except ImportError:
        print("Warning: langchain_ollama not installed. Running in fallback mode.")
        return None
    except Exception as e:
        print(f"Warning: Could not initialize Ollama LLM: {e}. Running in fallback mode.")
        return None


def setup_environment():
    """Setup environment variables from .env file if present."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
