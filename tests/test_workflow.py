"""Tests for agent workflow."""

from paper2skill.agents import SkillBuilderWorkflow


def test_workflow_without_llm():
    """Test workflow in fallback mode."""
    workflow = SkillBuilderWorkflow(llm=None)
    
    document_text = """
    # Test Paper
    
    This paper presents a novel algorithm.
    
    Theorem 1: The algorithm converges.
    
    We use Python and NumPy for implementation.
    
    Result: 50% improvement in performance.
    """
    
    state = workflow.run(document_text, "test.md")
    
    # Check that state has expected keys
    assert "understanding" in state
    assert "main_concepts" in state
    assert "theorems" in state
    assert "tools" in state
    assert "results" in state
    
    # Check that some extraction happened
    assert state["understanding"] is not None
    assert isinstance(state["main_concepts"], list)
    assert isinstance(state["theorems"], list)
    assert isinstance(state["tools"], list)
    assert isinstance(state["results"], list)
