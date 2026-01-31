"""State definitions for the multi-agent system."""

from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict):
    """State shared across all agents in the workflow."""
    
    # Input
    document_text: str
    document_path: str
    
    # Processing stages
    understanding: Optional[str]
    main_concepts: Optional[List[str]]
    theorems: Optional[List[Dict[str, str]]]
    tools: Optional[List[Dict[str, str]]]
    results: Optional[List[Dict[str, str]]]
    
    # Output
    skill_markdown: Optional[str]
    
    # Metadata
    error: Optional[str]
