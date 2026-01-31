"""Multi-agent workflow using LangGraph."""

from typing import Optional
from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import (
    DocumentUnderstandingAgent,
    ConceptExtractionAgent,
    ToolIdentificationAgent,
)


class SkillBuilderWorkflow:
    """Multi-agent workflow for building skills from documents."""

    def __init__(self, llm=None):
        """
        Initialize the skill builder workflow.
        
        Args:
            llm: Optional language model for agents
        """
        self.llm = llm
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        # Create workflow
        workflow = StateGraph(AgentState)

        # Create agents
        understanding_agent = DocumentUnderstandingAgent(self.llm)
        concept_agent = ConceptExtractionAgent(self.llm)
        tool_agent = ToolIdentificationAgent(self.llm)

        # Add nodes
        workflow.add_node("understand", understanding_agent)
        workflow.add_node("extract_concepts", concept_agent)
        workflow.add_node("identify_tools", tool_agent)

        # Define edges
        workflow.set_entry_point("understand")
        workflow.add_edge("understand", "extract_concepts")
        workflow.add_edge("extract_concepts", "identify_tools")
        workflow.add_edge("identify_tools", END)

        return workflow.compile()

    def run(self, document_text: str, document_path: str = "") -> AgentState:
        """
        Run the workflow on a document.
        
        Args:
            document_text: The text content of the document
            document_path: Path to the original document
            
        Returns:
            Final state with extracted information
        """
        initial_state: AgentState = {
            "document_text": document_text,
            "document_path": document_path,
            "understanding": None,
            "main_concepts": None,
            "theorems": None,
            "tools": None,
            "results": None,
            "skill_markdown": None,
            "error": None,
        }

        try:
            final_state = self.workflow.invoke(initial_state)
            return final_state
        except Exception as e:
            initial_state["error"] = str(e)
            return initial_state
