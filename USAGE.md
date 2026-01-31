# Example Usage Guide

This guide demonstrates various use cases for Paper2Skill.

## Basic Example

Let's process the included sample paper:

```bash
cd /home/runner/work/Paper2Skill/Paper2Skill
paper2skill examples/sample_paper.md
```

This will generate `sample_paper.skill.md` with extracted information.

## Advanced Examples

### 1. Processing a PDF Research Paper

```bash
paper2skill research_paper.pdf -o research_skill.md
```

### 2. Processing a Word Document

```bash
paper2skill technical_report.docx
```

### 3. Processing a PowerPoint Presentation

```bash
paper2skill conference_presentation.pptx --no-llm
```

### 4. Using Python API

```python
from paper2skill.loaders import MultiFormatLoader
from paper2skill.agents import SkillBuilderWorkflow
from paper2skill.generators import SkillMarkdownGenerator

# Load your document
doc_text = MultiFormatLoader.load("my_paper.pdf")

# Process with multi-agent system
workflow = SkillBuilderWorkflow(llm=None)  # or provide an LLM
state = workflow.run(doc_text, "my_paper.pdf")

# Generate Skill.md
output = SkillMarkdownGenerator.generate(state, "my_skill.md")
print(f"Generated: {len(output)} characters")
```

## Expected Output Structure

A typical Skill.md file includes:

```markdown
# Skill: [Document Title]

## Overview
Brief summary of the document

## Main Concepts
1. Concept A
2. Concept B
...

## Theorems and Propositions
### 1. Theorem Name
**Type:** theorem
**Description:** ...

## Tools and Methods
### 1. Tool Name
**Type:** library/framework/algorithm
**Description:** ...

## Key Results and Findings
...

## How to Use This Skill
Instructions for AI systems
```

## Customization

### Using Different LLM Models

```python
from langchain_openai import ChatOpenAI
from paper2skill.agents import SkillBuilderWorkflow

# Use GPT-4 for better analysis
llm = ChatOpenAI(model="gpt-4", temperature=0)
workflow = SkillBuilderWorkflow(llm=llm)
```

### Processing Multiple Documents

```python
import os
from pathlib import Path
from paper2skill.loaders import MultiFormatLoader
from paper2skill.agents import SkillBuilderWorkflow
from paper2skill.generators import SkillMarkdownGenerator

# Process all markdown files in a directory
doc_dir = Path("papers")
workflow = SkillBuilderWorkflow()

for doc_file in doc_dir.glob("*.md"):
    print(f"Processing {doc_file}")
    
    text = MultiFormatLoader.load(doc_file)
    state = workflow.run(text, str(doc_file))
    
    output_path = doc_file.with_suffix(".skill.md")
    SkillMarkdownGenerator.generate(state, output_path)
    
    print(f"✓ Generated {output_path}")
```

## Troubleshooting

### Issue: "OPENAI_API_KEY not found"

**Solution**: Either:
1. Set the environment variable: `export OPENAI_API_KEY=your_key`
2. Create a `.env` file with the key
3. Use `--no-llm` flag for fallback mode

### Issue: "Unsupported file format"

**Solution**: Ensure your file has one of these extensions:
- `.pdf` - PDF documents
- `.docx` - Word documents
- `.pptx` - PowerPoint presentations
- `.md`, `.markdown` - Markdown files
- `.txt` - Text files

### Issue: Import errors

**Solution**: Install all dependencies:
```bash
pip install -r requirements.txt
```
