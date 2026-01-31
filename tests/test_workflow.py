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


def test_workflow_extracts_useful_value():
    """Test that workflow extracts useful value for building/implementing."""
    workflow = SkillBuilderWorkflow(llm=None)
    
    document_text = """
    # Research Paper on Transformer Architecture
    
    ## Introduction
    
    We introduce the Transformer Architecture (TF) for sequence modeling.
    
    ## The Transformer Architecture
    
    The Transformer Architecture works by:
    - Using self-attention mechanisms
    - Eliminating recurrence for parallel processing
    - Employing positional encoding
    
    ## Tools and Implementation
    
    - **PyTorch** for deep learning
    - **NumPy** for numerical operations
    
    ## Results
    
    Our approach achieves 30% improvement in translation quality.
    """
    
    state = workflow.run(document_text, "transformer.md")
    
    # Check that useful_value and implementation_guide are extracted
    assert "useful_value" in state
    assert "implementation_guide" in state
    
    # Check useful_value structure
    useful_value = state.get("useful_value")
    assert useful_value is not None
    assert "name" in useful_value
    assert "type" in useful_value
    assert "description" in useful_value
    assert "key_principles" in useful_value
    
    # Check implementation_guide structure
    implementation_guide = state.get("implementation_guide")
    assert implementation_guide is not None
    assert "steps" in implementation_guide
    assert "required_tools" in implementation_guide
    assert isinstance(implementation_guide["steps"], list)
    assert len(implementation_guide["steps"]) > 0


def test_workflow_identifies_named_algorithm():
    """Test that workflow correctly identifies named algorithms."""
    workflow = SkillBuilderWorkflow(llm=None)
    
    document_text = """
    # Distributed Optimization
    
    ## Main Contributions
    
    We introduce the Distributed Optimization Algorithm (DOA) that reduces complexity.
    
    ### The DOA Algorithm
    
    The algorithm works by partitioning the problem space.
    """
    
    state = workflow.run(document_text, "doa.md")
    
    useful_value = state.get("useful_value", {})
    assert "DOA" in useful_value.get("name", "")
    assert useful_value.get("type") == "algorithm"
