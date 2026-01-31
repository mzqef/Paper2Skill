#!/usr/bin/env python3
"""
Demonstration script for Paper2Skill functionality.

This script shows various use cases and features of the Paper2Skill system.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from paper2skill.loaders import MultiFormatLoader
from paper2skill.agents import SkillBuilderWorkflow
from paper2skill.generators import SkillMarkdownGenerator


def demo_basic_usage():
    """Demonstrate basic document processing."""
    print("=" * 60)
    print("DEMO 1: Basic Document Processing")
    print("=" * 60)
    
    # Load the sample document
    doc_path = Path(__file__).parent.parent / "examples" / "sample_paper.md"
    print(f"\n1. Loading document: {doc_path.name}")
    
    text = MultiFormatLoader.load(doc_path)
    print(f"   ✓ Loaded {len(text)} characters")
    
    # Process with workflow
    print("\n2. Running multi-agent workflow...")
    workflow = SkillBuilderWorkflow(llm=None)
    state = workflow.run(text, str(doc_path))
    
    print(f"   ✓ Understanding extracted")
    print(f"   ✓ Found {len(state.get('main_concepts', []))} concepts")
    print(f"   ✓ Found {len(state.get('theorems', []))} theorems")
    print(f"   ✓ Found {len(state.get('tools', []))} tools")
    print(f"   ✓ Found {len(state.get('results', []))} results")
    
    # Generate output
    print("\n3. Generating Skill.md...")
    markdown = SkillMarkdownGenerator.generate(state)
    print(f"   ✓ Generated {len(markdown)} characters")
    
    print("\n✓ Demo 1 Complete!\n")


def demo_extraction_details():
    """Show detailed extraction results."""
    print("=" * 60)
    print("DEMO 2: Detailed Extraction Results")
    print("=" * 60)
    
    doc_path = Path(__file__).parent.parent / "examples" / "sample_paper.md"
    text = MultiFormatLoader.load(doc_path)
    
    workflow = SkillBuilderWorkflow(llm=None)
    state = workflow.run(text, str(doc_path))
    
    # Show concepts
    print("\nExtracted Concepts:")
    for i, concept in enumerate(state.get('main_concepts', []), 1):
        print(f"  {i}. {concept[:80]}...")
    
    # Show theorems
    print("\nExtracted Theorems:")
    for i, theorem in enumerate(state.get('theorems', []), 1):
        name = theorem.get('name', 'Unknown')
        print(f"  {i}. {name[:80]}...")
    
    # Show tools
    print("\nExtracted Tools (sample):")
    for i, tool in enumerate(state.get('tools', [])[:3], 1):
        name = tool.get('name', 'Unknown')
        print(f"  {i}. {name[:80]}...")
    
    print("\n✓ Demo 2 Complete!\n")


def demo_custom_output():
    """Demonstrate custom output path."""
    print("=" * 60)
    print("DEMO 3: Custom Output Path")
    print("=" * 60)
    
    doc_path = Path(__file__).parent.parent / "examples" / "sample_paper.md"
    output_path = "/tmp/custom_skill_demo.md"
    
    print(f"\n1. Processing: {doc_path.name}")
    print(f"2. Custom output: {output_path}")
    
    text = MultiFormatLoader.load(doc_path)
    workflow = SkillBuilderWorkflow(llm=None)
    state = workflow.run(text, str(doc_path))
    
    SkillMarkdownGenerator.generate(state, output_path)
    
    # Verify output
    output_file = Path(output_path)
    if output_file.exists():
        size = output_file.stat().st_size
        print(f"\n✓ File created: {output_path}")
        print(f"✓ File size: {size} bytes")
        output_file.unlink()  # Clean up
    
    print("\n✓ Demo 3 Complete!\n")


def demo_supported_formats():
    """Show supported document formats."""
    print("=" * 60)
    print("DEMO 4: Supported Formats")
    print("=" * 60)
    
    from paper2skill.loaders.document_loader import MultiFormatLoader
    
    print("\nSupported document formats:")
    for ext, loader_class in MultiFormatLoader.LOADERS.items():
        print(f"  {ext:12} - {loader_class.__name__}")
    
    print("\n✓ Demo 4 Complete!\n")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 60)
    print("Paper2Skill Demonstration Suite")
    print("=" * 60 + "\n")
    
    try:
        demo_basic_usage()
        demo_extraction_details()
        demo_custom_output()
        demo_supported_formats()
        
        print("=" * 60)
        print("All Demonstrations Complete!")
        print("=" * 60)
        print("\nTry it yourself:")
        print("  python -m paper2skill.main examples/sample_paper.md")
        print("\n")
        
    except Exception as e:
        print(f"\n✗ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
