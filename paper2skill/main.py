"""Main entry point for Paper2Skill."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from paper2skill.loaders import MultiFormatLoader
from paper2skill.agents import SkillBuilderWorkflow
from paper2skill.generators import SkillMarkdownGenerator
from paper2skill.utils import get_llm, setup_environment


def process_document(
    input_path: str,
    output_path: str = None,
    use_llm: bool = True,
    model: Optional[str] = None,
    config_path: Optional[str] = None
):
    """
    Process a document and generate a Skill.md file.
    
    Args:
        input_path: Path to the input document
        output_path: Path for the output Skill.md file
        use_llm: Whether to use LLM for enhanced processing
        model: Name of the model configuration to use (from config file)
        config_path: Path to configuration file
    """
    # Setup environment
    setup_environment()
    
    # Load document
    print(f"Loading document: {input_path}")
    try:
        document_text = MultiFormatLoader.load(input_path)
        print(f"✓ Document loaded successfully ({len(document_text)} characters)")
    except Exception as e:
        print(f"✗ Error loading document: {e}")
        sys.exit(1)
    
    # Initialize LLM if requested
    llm = None
    if use_llm:
        model_display = model if model else "default"
        print(f"Initializing language model ({model_display})...")
        llm = get_llm(model_name=model, config_path=config_path)
        if llm:
            print("✓ Language model initialized")
        else:
            print("⚠ Running in fallback mode without LLM")
    else:
        print("Running in fallback mode (--no-llm specified)")
    
    # Run workflow
    print("Running multi-agent analysis...")
    workflow = SkillBuilderWorkflow(llm=llm)
    
    try:
        state = workflow.run(document_text, input_path)
        
        if state.get("error"):
            print(f"✗ Error during processing: {state['error']}")
            sys.exit(1)
        
        print("✓ Analysis complete")
        
        # Print summary
        print("\nExtracted Information:")
        print(f"  - Concepts: {len(state.get('main_concepts', []))}")
        print(f"  - Theorems: {len(state.get('theorems', []))}")
        print(f"  - Tools: {len(state.get('tools', []))}")
        print(f"  - Results: {len(state.get('results', []))}")
        
    except Exception as e:
        print(f"✗ Error running workflow: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Generate output
    if output_path is None:
        input_stem = Path(input_path).stem
        output_path = f"{input_stem}.skill.md"
    
    print(f"\nGenerating Skill.md: {output_path}")
    try:
        markdown = SkillMarkdownGenerator.generate(state, output_path)
        print(f"✓ Skill.md generated successfully")
        print(f"\nOutput saved to: {output_path}")
        print(f"File size: {len(markdown)} characters")
    except Exception as e:
        print(f"✗ Error generating Skill.md: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Paper2Skill: Transform documents into AI-readable Skill.md files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  paper2skill document.pdf
  paper2skill paper.docx -o custom_output.md
  paper2skill presentation.pptx --no-llm
  paper2skill paper.pdf --model anthropic
  paper2skill paper.pdf --config /path/to/config.yaml
  
Supported formats: PDF, Word (.docx), PowerPoint (.pptx), Markdown (.md)

Model Configuration:
  Create a config.yaml file to configure multiple AI models.
  See config.example.yaml for available options.
        """
    )
    
    parser.add_argument(
        "input",
        help="Path to input document (PDF, Word, PowerPoint, or Markdown)"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Path to output Skill.md file (default: <input_name>.skill.md)",
        default=None
    )
    
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Run without language model (fallback mode)"
    )
    
    parser.add_argument(
        "--model", "-m",
        help="Model configuration to use from config file (e.g., openai, anthropic, azure)",
        default=None
    )
    
    parser.add_argument(
        "--config", "-c",
        help="Path to configuration file (default: searches for config.yaml)",
        default=None
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Paper2Skill 0.1.0"
    )
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    # Process document
    process_document(
        input_path=args.input,
        output_path=args.output,
        use_llm=not args.no_llm,
        model=args.model,
        config_path=args.config
    )


if __name__ == "__main__":
    main()
