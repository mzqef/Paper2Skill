# Architecture Documentation

## System Overview

Paper2Skill is a multi-agent system built on the LangChain/LangGraph ecosystem that transforms academic papers and technical documents into structured, AI-readable Skill.md files.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Input Layer                               │
├─────────────────────────────────────────────────────────────────┤
│  PDF  │  Word (.docx)  │  PowerPoint (.pptx)  │  Markdown (.md) │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Document Loader                               │
│                  (MultiFormatLoader)                             │
├─────────────────────────────────────────────────────────────────┤
│  - PDFLoader (pypdf)                                            │
│  - WordLoader (python-docx)                                     │
│  - PowerPointLoader (python-pptx)                               │
│  - MarkdownLoader (native)                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼ (Document Text)
┌─────────────────────────────────────────────────────────────────┐
│                  LangGraph Workflow                              │
│                (SkillBuilderWorkflow)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  1. Document Understanding Agent                         │  │
│  │     - Analyzes overall structure                         │  │
│  │     - Identifies main topics                             │  │
│  │     - Generates document summary                         │  │
│  └───────────────────┬──────────────────────────────────────┘  │
│                      │                                          │
│                      ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  2. Concept Extraction Agent                             │  │
│  │     - Extracts main concepts                             │  │
│  │     - Identifies theorems and lemmas                     │  │
│  │     - Extracts key results and findings                  │  │
│  └───────────────────┬──────────────────────────────────────┘  │
│                      │                                          │
│                      ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  3. Tool Identification Agent                            │  │
│  │     - Identifies algorithms and methods                  │  │
│  │     - Recognizes libraries and frameworks                │  │
│  │     - Detects techniques (even if not yet implemented)   │  │
│  └───────────────────┬──────────────────────────────────────┘  │
│                      │                                          │
└──────────────────────┼──────────────────────────────────────────┘
                       │
                       ▼ (Structured State)
┌─────────────────────────────────────────────────────────────────┐
│               Skill.md Generator                                 │
│            (SkillMarkdownGenerator)                              │
├─────────────────────────────────────────────────────────────────┤
│  - Template-based generation                                    │
│  - Formats concepts, theorems, tools, results                   │
│  - Creates self-contained AI instructions                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Output: Skill.md                              │
├─────────────────────────────────────────────────────────────────┤
│  - Overview and summary                                         │
│  - Main concepts                                                │
│  - Theorems and propositions                                   │
│  - Tools and methods                                            │
│  - Key results                                                  │
│  - Usage instructions for AI systems                            │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Document Loaders (`paper2skill/loaders/`)

**Purpose**: Extract text from various document formats.

**Components**:
- `MultiFormatLoader`: Automatic format detection and delegation
- `PDFLoader`: Extracts text from PDF files using pypdf
- `WordLoader`: Processes .docx files using python-docx
- `PowerPointLoader`: Extracts text from .pptx presentations
- `MarkdownLoader`: Handles markdown and text files

**Key Features**:
- Automatic format detection based on file extension
- Unified interface for all formats
- Error handling for missing dependencies

### 2. Multi-Agent System (`paper2skill/agents/`)

**Purpose**: Analyze documents using specialized agents in a workflow.

**Components**:

#### a. State Management (`state.py`)
- `AgentState`: TypedDict defining shared state across agents
- Tracks document text, extracted information, and metadata
- Includes `useful_value` and `implementation_guide` for actionable output

#### b. Agent Nodes (`nodes.py`)

**DocumentUnderstandingAgent**:
- Analyzes overall document structure
- Identifies main topics and themes
- Generates comprehensive understanding
- Supports both LLM and fallback modes

**ConceptExtractionAgent**:
- Extracts main concepts
- Identifies theorems, lemmas, propositions
- Extracts key results and findings
- Returns structured data (JSON)

**ToolIdentificationAgent**:
- Identifies algorithms and methods
- Recognizes libraries and frameworks
- Extracts tool names and descriptions
- Provides tool type classification

**ValueExtractionAgent** (NEW):
- Identifies WHAT IS USEFUL from the paper
- Extracts the core algorithm, model, or architecture
- Determines prerequisites and key principles
- Focuses on buildable/implementable value

**ImplementationGuideAgent** (NEW):
- Generates actionable implementation steps
- Identifies required tools and resources
- Creates validation criteria
- Produces external resource references

#### c. Workflow (`workflow.py`)
- `SkillBuilderWorkflow`: LangGraph-based orchestration
- Defines agent execution order
- Manages state transitions
- Handles errors gracefully

**Workflow Sequence**:
```
understand → extract_concepts → identify_tools → extract_value → generate_implementation → END
```

### 3. Skill.md Generator (`paper2skill/generators/`)

**Purpose**: Generate actionable, AI-readable Skill.md files focused on building/implementing.

**Components**:
- `SkillMarkdownGenerator`: Main generator class
- Action-oriented template
- Formats extracted information into implementation-focused sections

**Output Sections**:
1. **What You Will Build**: Core useful thing to implement
2. **Why This Is Useful**: Value proposition
3. **Prerequisites**: Required knowledge and background
4. **Core Principles**: Key concepts that make it work
5. **Implementation Guide**: Step-by-step build instructions
6. **Required Tools**: Libraries, frameworks, dependencies
7. **External Resources**: References and additional materials
8. **Validation Criteria**: How to verify success
9. **Theoretical Foundation**: Supporting theorems
10. **Expected Results**: Documented benchmarks

### 4. Utilities (`paper2skill/utils/`)

**Purpose**: Support functions for the system.

**Components**:
- `get_llm()`: LLM initialization with fallback
- `setup_environment()`: Environment configuration

### 5. Main Application (`paper2skill/main.py`)

**Purpose**: CLI interface and orchestration.

**Features**:
- Command-line argument parsing
- Document processing pipeline
- Progress reporting
- Error handling

## Data Flow

1. **Input**: User provides a document path
2. **Loading**: MultiFormatLoader extracts text
3. **Understanding**: DocumentUnderstandingAgent analyzes structure
4. **Extraction**: ConceptExtractionAgent finds concepts, theorems, results
5. **Tool Identification**: ToolIdentificationAgent recognizes methods/tools
6. **Value Extraction**: ValueExtractionAgent identifies what is useful (core algorithm, model, idea)
7. **Implementation Guide**: ImplementationGuideAgent generates actionable build steps
8. **Generation**: SkillMarkdownGenerator creates action-oriented Skill.md
9. **Output**: Self-contained, implementation-focused Skill.md file saved

## LLM Integration

### Two Operating Modes

#### 1. LLM-Enhanced Mode
- Uses OpenAI's GPT models via LangChain
- Better understanding and extraction
- More accurate concept identification
- Requires OPENAI_API_KEY

#### 2. Fallback Mode
- Rule-based extraction
- Keyword matching
- Pattern recognition
- No API key required
- Graceful degradation

### LLM Usage
```python
from paper2skill.utils import get_llm

# Initialize LLM
llm = get_llm(model_name="gpt-3.5-turbo")

# Use in workflow
workflow = SkillBuilderWorkflow(llm=llm)
```

## State Management

The system uses a shared state object (TypedDict) that flows through the workflow:

```python
AgentState = {
    "document_text": str,        # Input text
    "document_path": str,        # Source path
    "understanding": str,        # Overall analysis
    "main_concepts": List[str],  # Extracted concepts
    "theorems": List[Dict],      # Theorems/lemmas
    "tools": List[Dict],         # Tools/methods
    "results": List[Dict],       # Key findings
    "useful_value": Dict,        # Core useful thing (algorithm, model, etc.)
    "implementation_guide": Dict, # Steps, tools, resources for building
    "skill_markdown": str,       # Generated output
    "error": str                 # Error tracking
}
```

## Extension Points

### Adding New Document Formats

1. Create a new loader class inheriting from `DocumentLoader`
2. Implement the `load()` method
3. Register in `MultiFormatLoader.LOADERS`

```python
class NewFormatLoader(DocumentLoader):
    def load(self, file_path):
        # Implementation
        return text
        
MultiFormatLoader.LOADERS['.ext'] = NewFormatLoader
```

### Adding New Agents

1. Create agent class in `nodes.py`
2. Add to workflow in `workflow.py`
3. Update `AgentState` if needed

```python
class NewAgent:
    def __call__(self, state):
        # Process state
        return {"new_field": value}
        
# In workflow
workflow.add_node("new_agent", NewAgent())
workflow.add_edge("previous", "new_agent")
```

### Customizing Output Template

Modify `SkillMarkdownGenerator.TEMPLATE` to change the output format.

## Testing

### Test Structure
```
tests/
├── test_loaders.py     # Document loader tests
├── test_generators.py  # Generator tests
└── test_workflow.py    # Workflow integration tests
```

### Running Tests
```bash
pytest tests/ -v
```

## Dependencies

### Core
- `langchain`: LLM integration
- `langgraph`: Multi-agent orchestration
- `pydantic`: Data validation

### Document Processing
- `pypdf`: PDF support
- `python-docx`: Word support
- `python-pptx`: PowerPoint support

### Optional
- `langchain-openai`: OpenAI integration
- `python-dotenv`: Environment management

## Performance Considerations

1. **Document Size**: Large documents may take longer to process
2. **LLM Latency**: API calls add processing time
3. **Fallback Mode**: Faster but less accurate
4. **Memory**: Keep extracted text in memory during processing

## Security Considerations

1. **API Keys**: Store in environment variables, never in code
2. **File Validation**: Check file extensions and sizes
3. **Input Sanitization**: Handle malformed documents gracefully
4. **Output Validation**: Ensure generated markdown is safe

## Future Enhancements

Potential improvements:
- Streaming output for large documents
- Batch processing multiple documents
- Custom agent configurations
- Advanced NLP for concept extraction
- Graph visualization of concepts
- Interactive Skill.md editing
