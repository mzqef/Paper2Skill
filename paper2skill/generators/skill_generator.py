"""Generator for creating Skill.md files."""

from typing import Dict, Any, List
from datetime import datetime, timezone
from pathlib import Path


class SkillMarkdownGenerator:
    """Generator for creating self-contained Skill.md files focused on building/implementing."""

    TEMPLATE = """# Skill: {skill_name}

**Type:** {skill_type}  
**Generated from:** {source_document}  
**Generated on:** {timestamp}

---

## What You Will Build

{what_you_will_build}

---

## Why This Is Useful

{why_useful}

---

## Prerequisites

{prerequisites_section}

---

## Core Principles

{core_principles_section}

---

## Implementation Guide

{implementation_steps_section}

---

## Required Tools and Resources

{tools_section}

---

## External Resources

{external_resources_section}

---

## Validation Criteria

{validation_criteria_section}

---

## Supporting Concepts

{concepts_section}

---

## Theoretical Foundation

{theorems_section}

---

## Expected Results

{results_section}

---

## Quick Start

To implement this skill:

1. Review the **Prerequisites** to ensure you have the necessary background
2. Study the **Core Principles** to understand the fundamental concepts
3. Follow the **Implementation Guide** step by step
4. Use the **Required Tools** as specified
5. Validate your implementation against the **Validation Criteria**

---

## Notes for AI Systems

This skill document is designed to be actionable and self-contained:

- Focus on the **Implementation Guide** for step-by-step instructions
- Use **Core Principles** to understand the underlying theory
- Reference **External Resources** for additional context if needed
- The goal is to BUILD and IMPLEMENT, not just understand

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
        useful_value = state.get("useful_value", {}) or {}
        implementation_guide = state.get("implementation_guide", {}) or {}

        # Extract skill information
        skill_name = useful_value.get("name", cls._generate_title(document_path))
        skill_type = useful_value.get("type", "skill")
        what_you_will_build = useful_value.get("description", cls._generate_overview(understanding, concepts))
        why_useful = useful_value.get("why_useful", "This provides reusable knowledge that can be applied to solve problems in this domain.")
        key_principles = useful_value.get("key_principles", [])
        prerequisites = useful_value.get("prerequisites", [])

        # Extract implementation guide information
        impl_steps = implementation_guide.get("steps", [])
        required_tools = implementation_guide.get("required_tools", [])
        external_resources = implementation_guide.get("external_resources", [])
        validation_criteria = implementation_guide.get("validation_criteria", [])

        # Generate sections
        prerequisites_section = cls._format_prerequisites(prerequisites)
        core_principles_section = cls._format_core_principles(key_principles, concepts)
        implementation_steps_section = cls._format_implementation_steps(impl_steps)
        tools_section = cls._format_tools(tools, required_tools)
        external_resources_section = cls._format_external_resources(external_resources)
        validation_criteria_section = cls._format_validation_criteria(validation_criteria)
        concepts_section = cls._format_concepts(concepts)
        theorems_section = cls._format_theorems(theorems)
        results_section = cls._format_results(results)

        # Fill template
        markdown_content = cls.TEMPLATE.format(
            skill_name=skill_name,
            skill_type=skill_type.title(),
            source_document=document_path,
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            what_you_will_build=what_you_will_build,
            why_useful=why_useful,
            prerequisites_section=prerequisites_section,
            core_principles_section=core_principles_section,
            implementation_steps_section=implementation_steps_section,
            tools_section=tools_section,
            external_resources_section=external_resources_section,
            validation_criteria_section=validation_criteria_section,
            concepts_section=concepts_section,
            theorems_section=theorems_section,
            results_section=results_section,
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
            # Take first few sentences from understanding, filtering empty strings
            sentences = [s.strip() for s in understanding.split('.')[:3] if s.strip()]
            if sentences:
                overview_parts.append('.'.join(sentences) + '.')
        
        if concepts and len(concepts) > 0:
            overview_parts.append(
                f"\n\nThis document covers {len(concepts)} main concepts and provides "
                "comprehensive analysis of the subject matter."
            )
        
        return '\n'.join(overview_parts) if overview_parts else "No overview available."

    @staticmethod
    def _format_prerequisites(prerequisites: List[str]) -> str:
        """Format the prerequisites section."""
        if not prerequisites:
            return "- Basic programming knowledge\n- Understanding of the problem domain"
        
        formatted = []
        for prereq in prerequisites:
            formatted.append(f"- {prereq}")
        
        return '\n'.join(formatted)

    @staticmethod
    def _format_core_principles(key_principles: List[str], concepts: List[str]) -> str:
        """Format the core principles section."""
        principles = key_principles if key_principles else concepts[:5]
        
        if not principles:
            return "*Core principles will be derived from the implementation.*"
        
        formatted = []
        for i, principle in enumerate(principles, 1):
            formatted.append(f"{i}. **{principle}**")
        
        return '\n'.join(formatted)

    @staticmethod
    def _format_implementation_steps(steps: List[Dict[str, Any]]) -> str:
        """Format the implementation steps section."""
        if not steps:
            return """### Step 1: Understand the Core Concepts
Review the core principles and prerequisites before implementing.

### Step 2: Set Up Environment
Install required tools and dependencies.

### Step 3: Implement Core Logic
Build the main components following the principles.

### Step 4: Test and Validate
Verify implementation against validation criteria."""
        
        formatted = []
        for step in steps:
            step_num = step.get("step", 0)
            title = step.get("title", f"Step {step_num}")
            description = step.get("description", "")
            details = step.get("details", "")
            
            formatted.append(f"### Step {step_num}: {title}\n")
            if description:
                formatted.append(f"**Goal:** {description}\n")
            if details:
                formatted.append(f"{details}\n")
        
        return '\n'.join(formatted)

    @staticmethod
    def _format_tools(tools: List[Dict[str, str]], required_tools: List[str]) -> str:
        """Format the tools section."""
        formatted = []
        
        # First list required tools from implementation guide
        if required_tools:
            formatted.append("### Required for Implementation\n")
            for tool in required_tools:
                formatted.append(f"- **{tool}**")
            formatted.append("")
        
        # Then list tools from document
        if tools:
            formatted.append("### Tools from Document\n")
            for i, tool in enumerate(tools, 1):
                name = tool.get("name", f"Tool {i}")
                description = tool.get("description", "No description available")
                tool_type = tool.get("type", "tool")
                
                formatted.append(f"**{i}. {name}** ({tool_type})")
                formatted.append(f"   {description}\n")
        
        if not formatted:
            return "*No specific tools identified. Use appropriate tools for your implementation language.*"
        
        return '\n'.join(formatted)

    @staticmethod
    def _format_external_resources(resources: List[str]) -> str:
        """Format external resources section."""
        if not resources:
            return "- Original paper/document for detailed specifications\n- Related implementations for reference"
        
        formatted = []
        for resource in resources:
            formatted.append(f"- {resource}")
        
        return '\n'.join(formatted)

    @staticmethod
    def _format_validation_criteria(criteria: List[str]) -> str:
        """Format validation criteria section."""
        if not criteria:
            return "- Implementation produces expected outputs\n- Performance matches documented benchmarks\n- All core features are functional"
        
        formatted = []
        for i, criterion in enumerate(criteria, 1):
            formatted.append(f"{i}. {criterion}")
        
        return '\n'.join(formatted)

    @staticmethod
    def _format_concepts(concepts: List[str]) -> str:
        """Format the concepts section."""
        if not concepts:
            return "*No additional concepts extracted.*"
        
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
    def _format_results(results: List[Dict[str, str]]) -> str:
        """Format the results section."""
        if not results:
            return "*No specific results documented.*"
        
        formatted = []
        for i, result in enumerate(results, 1):
            description = result.get("description", "No description")
            result_type = result.get("type", "result")
            
            formatted.append(f"### Result {i}\n")
            formatted.append(f"**Type:** {result_type}\n")
            formatted.append(f"**Finding:** {description}\n")
        
        return '\n'.join(formatted)
