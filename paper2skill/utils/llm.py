"""Utility functions for Paper2Skill."""

import os
from typing import Optional


def get_llm(model_name: str = "gpt-3.5-turbo"):
    """
    Get a language model instance.
    
    Args:
        model_name: Name of the model to use
        
    Returns:
        Language model instance or None if API key not available
    """
    try:
        from langchain_openai import ChatOpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Warning: OPENAI_API_KEY not found. Running in fallback mode.")
            return None
        
        return ChatOpenAI(model=model_name, temperature=0)
    except ImportError:
        print("Warning: langchain_openai not installed. Running in fallback mode.")
        return None
    except Exception as e:
        print(f"Warning: Could not initialize LLM: {e}. Running in fallback mode.")
        return None


def setup_environment():
    """Setup environment variables from .env file if present."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
