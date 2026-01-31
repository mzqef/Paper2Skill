"""Generator for creating Skill.md files."""

from typing import Dict, Any, List
from datetime import datetime, timezone
from pathlib import Path


class SkillMarkdownGenerator:
    """Generator for creating self-contained Skill.md files."""

    TEMPLATE = """# Skill: {title}

**Generated from:** {source_document}  
**Generated on:** {timestamp}

---

## Overview

{overview}

---

## Main Concepts

{concepts_section}

---

## Theorems and Propositions

{theorems_section}

---

## Tools and Methods

{tools_section}

---

## Key Results and Findings

{results_section}

---

## How to Use This Skill

This skill document is designed to be used by AI systems to understand and reproduce the work described in the source document.

### For AI Systems:

1. **Understanding**: Read the overview and main concepts to grasp the domain
2. **Implementation**: Use the tools and methods section to implement solutions
3. **Validation**: Apply theorems and propositions to validate results
4. **Reproduction**: Follow the key results to reproduce findings

### Required Capabilities:

- Understanding of technical and mathematical content
- Ability to work with described tools (even if not yet implemented)
- Capability to apply theoretical concepts to practical problems

---

## Source Document Analysis

**Document Understanding:**
{understanding}

---

## Additional Notes

- This skill is self-contained and includes all necessary information
- Tools mentioned may be conceptual or not yet implemented
- AI systems should adapt techniques to available resources
- Results should be validated against the theorems and propositions

---

*End of Skill Document*
"""

    @classmethod
    def generate(cls, state: Dict[str, Any], output_path: str = None) -> str:
        """
        Generate a Skill.md file from the agent state.
        
        Args:
            state: The final state from the agent workflow
            output_path: Optional path to save the markdown file
            
        Returns:
            The generated markdown content
        """
        # Extract data from state
        document_path = state.get("document_path", "Unknown")
        understanding = state.get("understanding", "No understanding available")
        concepts = state.get("main_concepts", [])
        theorems = state.get("theorems", [])
        tools = state.get("tools", [])
        results = state.get("results", [])

        # Generate title from document path
        title = cls._generate_title(document_path)

        # Generate sections
        concepts_section = cls._format_concepts(concepts)
        theorems_section = cls._format_theorems(theorems)
        tools_section = cls._format_tools(tools)
        results_section = cls._format_results(results)
        overview = cls._generate_overview(understanding, concepts)

        # Fill template
        markdown_content = cls.TEMPLATE.format(
            title=title,
            source_document=document_path,
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            overview=overview,
            concepts_section=concepts_section,
            theorems_section=theorems_section,
            tools_section=tools_section,
            results_section=results_section,
            understanding=understanding,
        )

        # Save if output path provided
        if output_path:
            Path(output_path).write_text(markdown_content, encoding='utf-8')

        return markdown_content

    @staticmethod
    def _generate_title(document_path: str) -> str:
        """Generate a title from the document path."""
        if document_path and document_path != "Unknown":
            # Extract filename without extension
            path = Path(document_path)
            title = path.stem.replace('_', ' ').replace('-', ' ').title()
            return title
        return "Document Analysis"

    @staticmethod
    def _generate_overview(understanding: str, concepts: List[str]) -> str:
        """Generate an overview section."""
        overview_parts = []
        
        if understanding:
            # Take first few sentences from understanding
            sentences = understanding.split('.')[:3]
            overview_parts.append('.'.join(sentences) + '.')
        
        if concepts and len(concepts) > 0:
            overview_parts.append(
                f"\n\nThis document covers {len(concepts)} main concepts and provides "
                "comprehensive analysis of the subject matter."
            )
        
        return '\n'.join(overview_parts) if overview_parts else "No overview available."

    @staticmethod
    def _format_concepts(concepts: List[str]) -> str:
        """Format the concepts section."""
        if not concepts:
            return "*No main concepts extracted.*"
        
        formatted = []
        for i, concept in enumerate(concepts, 1):
            formatted.append(f"{i}. **{concept}**")
        
        return '\n'.join(formatted)

    @staticmethod
    def _format_theorems(theorems: List[Dict[str, str]]) -> str:
        """Format the theorems section."""
        if not theorems:
            return "*No theorems or propositions found.*"
        
        formatted = []
        for i, theorem in enumerate(theorems, 1):
            name = theorem.get("name", f"Theorem {i}")
            description = theorem.get("description", "No description")
            theorem_type = theorem.get("type", "theorem")
            
            formatted.append(f"### {i}. {name}\n")
            formatted.append(f"**Type:** {theorem_type}\n")
            formatted.append(f"**Description:** {description}\n")
        
        return '\n'.join(formatted)

    @staticmethod
    def _format_tools(tools: List[Dict[str, str]]) -> str:
        """Format the tools section."""
        if not tools:
            return "*No tools or methods identified.*"
        
        formatted = []
        for i, tool in enumerate(tools, 1):
            name = tool.get("name", f"Tool {i}")
            description = tool.get("description", "No description available")
            tool_type = tool.get("type", "tool")
            
            formatted.append(f"### {i}. {name}\n")
            formatted.append(f"**Type:** {tool_type}\n")
            formatted.append(f"**Description:** {description}\n")
            formatted.append("**Usage:** This tool can be used by AI systems even if not yet implemented. "
                           "Follow the description to create or simulate the functionality.\n")
        
        return '\n'.join(formatted)

    @staticmethod
    def _format_results(results: List[Dict[str, str]]) -> str:
        """Format the results section."""
        if not results:
            return "*No key results or findings extracted.*"
        
        formatted = []
        for i, result in enumerate(results, 1):
            description = result.get("description", "No description")
            result_type = result.get("type", "result")
            
            formatted.append(f"### Result {i}\n")
            formatted.append(f"**Type:** {result_type}\n")
            formatted.append(f"**Finding:** {description}\n")
        
        return '\n'.join(formatted)
