"""Tests for the skill generator."""

from pathlib import Path
from paper2skill.generators import SkillMarkdownGenerator


def test_skill_generation():
    """Test generating a Skill.md from state."""
    state = {
        "document_path": str(Path("test") / "sample.pdf"),
        "understanding": "This is a test document about algorithms.",
        "main_concepts": ["Algorithm Design", "Optimization", "Distributed Systems"],
        "theorems": [
            {
                "name": "Convergence Theorem",
                "description": "The algorithm converges",
                "type": "theorem"
            }
        ],
        "tools": [
            {
                "name": "NetworkX",
                "description": "Graph library",
                "type": "library"
            }
        ],
        "results": [
            {
                "description": "40% improvement",
                "type": "empirical"
            }
        ]
    }
    
    markdown = SkillMarkdownGenerator.generate(state)
    
    # Check that key sections are present
    assert "# Skill:" in markdown
    assert "Algorithm Design" in markdown
    assert "Convergence Theorem" in markdown
    assert "NetworkX" in markdown
    assert "40% improvement" in markdown


def test_empty_state():
    """Test generating from minimal state."""
    state = {
        "document_path": "test.md",
        "understanding": None,
        "main_concepts": [],
        "theorems": [],
        "tools": [],
        "results": []
    }
    
    markdown = SkillMarkdownGenerator.generate(state)
    
    # Should still generate valid markdown
    assert "# Skill:" in markdown
    assert "No main concepts" in markdown or "*No" in markdown
