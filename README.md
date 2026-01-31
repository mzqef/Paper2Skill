# Paper2Skill

An intelligent Agent Skill Builder that transforms academic papers and technical documents into actionable Skill.md files designed for AI systems.

## Overview

Paper2Skill uses a multi-agent system built on LangChain/LangGraph to analyze documents and extract **what is useful** - the core theory, algorithm, model, or idea that can be built or implemented. The output is a self-contained Skill.md file that provides step-by-step implementation guidance, not just a paper review.

**Key Philosophy:** The goal is to generate actionable skills. For example, from "Attention is All You Need," the system extracts how to **build a Transformer module**, not just summarize the paper.

## Features

✅ **Actionable Output**: Generates implementation guides with steps, tools, and validation criteria  
✅ **Value Extraction**: Identifies the core useful thing (algorithm, model, architecture) from papers  
✅ **Multi-Format Support**: Process PDF, Word (.docx), PowerPoint (.pptx), and Markdown documents  
✅ **LangChain/LangGraph Ecosystem**: Built on industry-standard AI frameworks  
✅ **Multi-Agent Analysis**: 5 specialized agents for understanding, extraction, and implementation guidance  
✅ **Tool Recognition**: Identifies required tools and libraries  
✅ **Self-Contained Output**: Generates comprehensive Skill.md files ready for AI consumption  
✅ **Fallback Mode**: Works without LLM for basic processing  

## Installation

### Using pip

```bash
pip install -e .
```

### Using requirements.txt

```bash
pip install -r requirements.txt
```

### Dependencies

- Python >= 3.9
- LangChain >= 0.1.0
- LangGraph >= 0.0.20
- pypdf >= 3.17.0 (for PDF support)
- python-docx >= 1.0.0 (for Word support)
- python-pptx >= 0.6.21 (for PowerPoint support)

## Quick Start

### Basic Usage

```bash
# Process a document (with LLM)
paper2skill examples/sample_paper.md

# Process without LLM (fallback mode)
paper2skill document.pdf --no-llm

# Specify custom output path
paper2skill paper.docx -o custom_output.md
```

### Using as a Library

```python
from paper2skill.loaders import MultiFormatLoader
from paper2skill.agents import SkillBuilderWorkflow
from paper2skill.generators import SkillMarkdownGenerator
from paper2skill.utils import get_llm, setup_environment

# Setup
setup_environment()

# Load document
document_text = MultiFormatLoader.load("paper.pdf")

# Run multi-agent workflow
llm = get_llm()  # Optional: None for fallback mode
workflow = SkillBuilderWorkflow(llm=llm)
state = workflow.run(document_text, "paper.pdf")

# Generate Skill.md
markdown = SkillMarkdownGenerator.generate(state, "output.skill.md")
```

## Architecture

### Multi-Agent System

The system uses a LangGraph-based workflow with 5 specialized agents:

1. **Document Understanding Agent**: Analyzes overall document structure and content
2. **Concept Extraction Agent**: Identifies main concepts, theorems, and results
3. **Tool Identification Agent**: Recognizes tools, methods, and techniques
4. **Value Extraction Agent**: Identifies what is USEFUL from the paper (core algorithm, model, architecture)
5. **Implementation Guide Agent**: Generates actionable steps to build/implement the useful thing

### Workflow

```
Document Input → Document Loader → Multi-Agent Analysis → Value Extraction → Implementation Guide → Skill.md Generation
```

## Configuration

### Environment Variables

Create a `.env` file for configuration:

```bash
# Optional: For enhanced LLM-powered analysis
OPENAI_API_KEY=your_api_key_here
```

Without an API key, the system runs in fallback mode with rule-based extraction.

## Output Format

The generated Skill.md is **action-oriented** and includes:

- **What You Will Build**: Description of the core useful thing
- **Why This Is Useful**: Value proposition and use cases
- **Prerequisites**: Required knowledge and background
- **Core Principles**: Key concepts that make it work
- **Implementation Guide**: Step-by-step instructions to build it
- **Required Tools**: Libraries, frameworks, and dependencies
- **External Resources**: References and additional materials
- **Validation Criteria**: How to verify the implementation works
- **Theoretical Foundation**: Supporting theorems and propositions
- **Expected Results**: Documented outcomes and benchmarks

## Examples

See the `examples/` directory for sample documents:

- `sample_paper.md`: Example research paper on distributed algorithms

### Running Examples

```bash
# Process the sample paper
paper2skill examples/sample_paper.md

# Output will be saved as sample_paper.skill.md
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run specific test file
pytest tests/test_loaders.py
```

### Project Structure

```
paper2skill/
├── agents/          # Multi-agent system
│   ├── nodes.py     # Agent implementations
│   ├── state.py     # Shared state definitions
│   └── workflow.py  # LangGraph workflow
├── loaders/         # Document loaders
│   └── document_loader.py
├── generators/      # Skill.md generation
│   └── skill_generator.py
├── utils/           # Utilities
│   └── llm.py
└── main.py          # CLI entry point
```

## Requirements Met

This implementation fulfills all specified requirements:

1. ✅ **LangChain/LangGraph Ecosystem**: Uses LangGraph for multi-agent orchestration
2. ✅ **Multiple Input Types**: Supports PDF, Word, Markdown, PowerPoint
3. ✅ **Value Extraction**: Identifies what is useful from papers (core algorithm, model, or idea)
4. ✅ **Implementation Guidance**: Generates actionable steps to build the useful thing
5. ✅ **Tool Handling**: Recognizes required tools and libraries
6. ✅ **Self-Contained Skill.md**: Generates comprehensive, actionable skill documents

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - See LICENSE file for details
