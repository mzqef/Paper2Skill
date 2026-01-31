"""Agent nodes for the multi-agent workflow."""

from typing import Dict, Any, List
import json

# Well-known libraries and tools that can be identified in documents
# This list can be extended as needed without modifying extraction logic
KNOWN_LIBRARIES = [
    "NumPy", "PyTorch", "TensorFlow", "NetworkX", "Redis", "Docker", "Kubernetes",
    "Pandas", "Scikit-learn", "Keras", "Flask", "Django", "FastAPI", "SQLAlchemy",
    "React", "Vue", "Angular", "Node", "Express", "MongoDB", "PostgreSQL", "MySQL"
]


class DocumentUnderstandingAgent:
    """Agent for understanding the overall document content and structure."""

    def __init__(self, llm=None):
        """Initialize the document understanding agent."""
        self.llm = llm

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and understand the document."""
        document_text = state.get("document_text", "")
        
        if not self.llm:
            # Fallback mode without LLM
            understanding = self._fallback_understanding(document_text)
        else:
            # Use LLM for understanding
            understanding = self._llm_understanding(document_text)
        
        return {
            "understanding": understanding,
        }
    
    def _fallback_understanding(self, text: str) -> str:
        """Provide basic understanding without LLM."""
        lines = text.split('\n')
        word_count = len(text.split())
        
        return f"""Document Analysis:
- Total words: {word_count}
- Total lines: {len(lines)}
- Document appears to contain technical/academic content
- Structure includes multiple sections and paragraphs
"""
    
    def _llm_understanding(self, text: str) -> str:
        """Use LLM to understand the document."""
        prompt = f"""Analyze this document and provide a comprehensive understanding:

Document:
{text[:3000]}...

Provide:
1. Main topic and purpose
2. Key themes
3. Target audience
4. Document structure overview
"""
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            return f"Error in LLM understanding: {str(e)}\n" + self._fallback_understanding(text)


class ConceptExtractionAgent:
    """Agent for extracting main concepts, theorems, and results."""

    def __init__(self, llm=None):
        """Initialize the concept extraction agent."""
        self.llm = llm

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract main concepts, theorems, and results from the document."""
        document_text = state.get("document_text", "")
        
        if not self.llm:
            # Fallback mode
            concepts, theorems, results = self._fallback_extraction(document_text)
        else:
            # Use LLM
            concepts, theorems, results = self._llm_extraction(document_text)
        
        return {
            "main_concepts": concepts,
            "theorems": theorems,
            "results": results,
        }
    
    def _fallback_extraction(self, text: str):
        """Extract concepts without LLM."""
        import re
        
        # Simple keyword-based extraction
        concepts = []
        theorems = []
        results = []
        seen_concepts = set()
        
        lines = text.split('\n')
        
        # Extract theorems and lemmas
        for line in lines:
            lower_line = line.lower()
            if any(keyword in lower_line for keyword in ['theorem', 'lemma', 'proposition']):
                # Extract the theorem name more cleanly
                match = re.search(r'\*\*([^*]+)\*\*', line)
                if match:
                    name = match.group(1)
                else:
                    name = line.strip()[:100]
                theorems.append({
                    "name": name,
                    "description": "Extracted from document",
                    "type": "theorem"
                })
        
        # Extract results - look for quantitative findings
        for line in lines:
            lower_line = line.lower()
            # Look for percentage improvements or quantitative results
            if re.search(r'\d+%', line) or any(kw in lower_line for kw in ['improvement', 'reduction', 'increase']):
                if not any(kw in lower_line for kw in ['theorem', 'lemma']):
                    results.append({
                        "description": line.strip().lstrip('-').strip()[:200],
                        "type": "empirical result"
                    })
        
        # Extract concepts from headings and bold items
        for line in lines:
            stripped = line.strip()
            # Extract from markdown headings (## or ###)
            if stripped.startswith('##'):
                concept = stripped.lstrip('#').strip()
                if concept and concept not in seen_concepts:
                    # Skip generic headings
                    if concept.lower() not in ['introduction', 'conclusion', 'results', 'methodology', 'references']:
                        seen_concepts.add(concept)
                        concepts.append(concept)
        
        # Also extract key bold terms as concepts
        bold_pattern = re.compile(r'\*\*([^*]+)\*\*')
        for match in bold_pattern.finditer(text):
            term = match.group(1).strip()
            # Keep only meaningful short terms
            if (2 <= len(term.split()) <= 5 and 
                term not in seen_concepts and
                not term.lower().startswith(('type:', 'result', 'finding'))):
                seen_concepts.add(term)
                concepts.append(term)
        
        return concepts[:10], theorems[:5], results[:5]
    
    def _llm_extraction(self, text: str):
        """Use LLM to extract concepts."""
        prompt = f"""Extract key information from this document:

Document:
{text[:4000]}...

Extract and format as JSON:
1. main_concepts: List of main concepts (strings)
2. theorems: List of theorems/lemmas (objects with name, description, type)
3. results: List of main results/findings (objects with description, type)

Return only valid JSON.
"""
        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Try to parse JSON
            try:
                data = json.loads(content)
                return (
                    data.get("main_concepts", []),
                    data.get("theorems", []),
                    data.get("results", [])
                )
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return self._fallback_extraction(text)
        except Exception:
            return self._fallback_extraction(text)


class ToolIdentificationAgent:
    """Agent for identifying tools, methods, and techniques used."""

    def __init__(self, llm=None):
        """Initialize the tool identification agent."""
        self.llm = llm

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Identify tools and methods from the document."""
        document_text = state.get("document_text", "")
        
        if not self.llm:
            tools = self._fallback_tool_identification(document_text)
        else:
            tools = self._llm_tool_identification(document_text)
        
        return {
            "tools": tools,
        }
    
    def _fallback_tool_identification(self, text: str):
        """Identify tools without LLM."""
        tools = []
        seen_names = set()
        
        # Look for specific tool patterns like "**Name**" or explicit tool mentions
        import re
        
        # Exclusion keywords - these are not tools
        exclude_keywords = [
            'result', 'finding', 'contribution', 'type', 'theorem', 'lemma', 
            'proposition', 'validation', 'empirical', 'novel', 'overview',
            'introduction', 'conclusion', 'methodology', 'abstract'
        ]
        
        # Pattern 1: Look for bold items in tool context (e.g., "- **Python 3.9** for...")
        lines = text.split('\n')
        for line in lines:
            stripped = line.strip()
            # Match "- **Name** for/:" pattern
            item_match = re.match(r'^[-*]\s*\*\*([^*]+)\*\*\s*(?:for|:|-|–)?\s*(.*)$', stripped)
            if item_match:
                name = item_match.group(1).strip()
                desc = item_match.group(2).strip() if item_match.group(2) else "Tool from document"
                lower_name = name.lower()
                # Only include if it looks like a tool/library name
                if (name not in seen_names and 
                    len(name.split()) <= 4 and
                    not any(kw in lower_name for kw in exclude_keywords)):
                    seen_names.add(name)
                    tools.append({
                        "name": name,
                        "description": desc,
                        "type": "tool/library"
                    })
        
        # Pattern 2: Look for algorithm/framework names in headings
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#'):
                # Extract heading text
                heading = stripped.lstrip('#').strip()
                lower_heading = heading.lower()
                if 'algorithm' in lower_heading and 'novel' not in lower_heading:
                    if heading not in seen_names:
                        seen_names.add(heading)
                        tools.append({
                            "name": heading,
                            "description": "Core algorithm described in document",
                            "type": "algorithm"
                        })
                elif 'framework' in lower_heading and heading not in seen_names:
                    seen_names.add(heading)
                    tools.append({
                        "name": heading,
                        "description": "Core framework described in document",
                        "type": "framework"
                    })
        
        # Pattern 3: Look for well-known library/tool names from the configurable list
        # Build regex pattern from KNOWN_LIBRARIES constant
        known_libs_pattern = r'\b(' + '|'.join(KNOWN_LIBRARIES) + r')\b'
        known_patterns = [
            r'\b(Python\s*\d+(?:\.\d+)?)\b',
            known_libs_pattern,
            r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b',  # CamelCase names like "TensorFlow"
        ]
        for pattern in known_patterns:
            for match in re.finditer(pattern, text):
                name = match.group(1)
                if name not in seen_names and len(name.split()) <= 3:
                    seen_names.add(name)
                    tools.append({
                        "name": name,
                        "description": "Library/tool mentioned in document",
                        "type": "library"
                    })
        
        return tools[:10]
    
    def _llm_tool_identification(self, text: str):
        """Use LLM to identify tools."""
        prompt = f"""Identify all tools, methods, algorithms, and techniques from this document:

Document:
{text[:4000]}...

For each tool/method, provide:
- name: The name of the tool/method
- description: What it does and how it's used
- type: Category (algorithm, framework, library, technique, etc.)

Return as JSON array. Include tools even if they don't exist yet but are described.
"""
        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            try:
                tools = json.loads(content)
                if isinstance(tools, list):
                    return tools
                return self._fallback_tool_identification(text)
            except json.JSONDecodeError:
                return self._fallback_tool_identification(text)
        except Exception:
            return self._fallback_tool_identification(text)


class ValueExtractionAgent:
    """Agent for extracting what is useful from the paper - the core theory/algorithm/model/idea."""

    def __init__(self, llm=None):
        """Initialize the value extraction agent."""
        self.llm = llm

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract the core useful value from the document."""
        document_text = state.get("document_text", "")
        understanding = state.get("understanding", "")
        main_concepts = state.get("main_concepts", [])
        theorems = state.get("theorems", [])
        tools = state.get("tools", [])
        
        if not self.llm:
            useful_value = self._fallback_value_extraction(
                document_text, understanding, main_concepts, theorems, tools
            )
        else:
            useful_value = self._llm_value_extraction(
                document_text, understanding, main_concepts, theorems, tools
            )
        
        return {
            "useful_value": useful_value,
        }
    
    def _fallback_value_extraction(self, text: str, understanding: str, 
                                    concepts: list, theorems: list, tools: list):
        """Extract useful value without LLM."""
        import re
        
        # Identify the most prominent algorithm/method/model from the document
        value_type = "algorithm"  # Default
        value_name = "Extracted Method"
        value_description = ""
        
        # More precise regex pattern for multi-word names
        # Matches: "Word Word Word" with proper capitalization
        multi_word_name = r'[A-Z][a-z]*(?:\s+[A-Z][a-z]*)*'
        
        # Look for key value indicators - prioritize named algorithms/models
        lines = text.split('\n')
        
        # First, try to find "introduce/present the X (ABC)" pattern
        for line in lines:
            # Pattern: "introduce/present the Name Algorithm (ABC)"
            match = re.search(
                rf'(?:introduce|present|propose)\s+the\s+({multi_word_name})\s*\(([A-Z]{{2,}})\)',
                line
            )
            if match:
                full_name = match.group(1).strip()
                acronym = match.group(2)
                value_name = f"{full_name} ({acronym})"
                break
            
            # Pattern: "the Name Algorithm (ABC) that..."
            match = re.search(
                rf'the\s+({multi_word_name}\s*(?:Algorithm|Model|Framework|Architecture))\s*\(([A-Z]{{2,}})\)',
                line
            )
            if match:
                full_name = match.group(1).strip()
                acronym = match.group(2)
                value_name = f"{full_name} ({acronym})"
                break
            
            # Pattern: "Name Algorithm/Model" without acronym
            match = re.search(
                rf'(?:the\s+)?({multi_word_name}\s*(?:Algorithm|Model|Framework|Architecture|Method))\b',
                line
            )
            if match and value_name == "Extracted Method":
                potential_name = match.group(1).strip()
                # Skip if it's just "Novel Algorithm" - look for more specific name
                if 'novel' not in potential_name.lower():
                    value_name = potential_name
        
        # If no specific name found, look in headings
        if value_name == "Extracted Method":
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('#'):
                    heading = stripped.lstrip('#').strip()
                    lower = heading.lower()
                    if 'algorithm' in lower and 'novel' not in lower:
                        value_name = heading
                        value_type = "algorithm"
                        break
                    elif 'model' in lower:
                        value_name = heading
                        value_type = "model"
                        break
                    elif 'framework' in lower:
                        value_name = heading
                        value_type = "framework"
                        break
        
        # Determine type based on name
        lower_name = value_name.lower()
        if 'algorithm' in lower_name:
            value_type = "algorithm"
        elif 'model' in lower_name:
            value_type = "model"
        elif 'framework' in lower_name:
            value_type = "framework"
        elif 'architecture' in lower_name:
            value_type = "architecture"
        
        # Build description - look for a sentence that describes what it does
        # Use the first part of value_name for matching
        name_parts = value_name.split()
        if name_parts:
            first_word = name_parts[0].lower()
            for line in lines:
                lower = line.lower()
                if first_word in lower and any(kw in lower for kw in ['introduce', 'present', 'propose', 'describe', 'works by']):
                    value_description = line.strip()
                    break
        
        if not value_description:
            # Look for a line that describes the approach
            for line in lines:
                lower = line.lower()
                if any(kw in lower for kw in ['this paper presents', 'we present', 'we propose', 'our approach']):
                    value_description = line.strip()
                    break
        
        if not value_description and understanding:
            # Extract first meaningful sentence from understanding
            sentences = [s.strip() for s in understanding.split('.') if s.strip() and len(s.strip()) > 20]
            if sentences:
                value_description = sentences[0] + '.'
        
        # Extract key principles from concepts
        principles = []
        for concept in concepts[:5]:
            if isinstance(concept, str) and len(concept) > 3:
                principles.append(concept)
        
        # If no principles found, extract from document structure
        if not principles:
            for line in lines:
                stripped = line.strip()
                # Look for bullet points or numbered items
                if stripped.startswith(('-', '*', '1.', '2.', '3.')):
                    clean = stripped.lstrip('-*0123456789.').strip()
                    if clean and len(clean) < 100:
                        principles.append(clean)
                        if len(principles) >= 5:
                            break
        
        return {
            "name": value_name,
            "type": value_type,
            "description": value_description if value_description else f"A {value_type} for solving problems in this domain.",
            "why_useful": "This provides a reusable approach that can be applied to similar problems.",
            "key_principles": principles if principles else ["See document for detailed principles"],
            "prerequisites": ["Understanding of the problem domain", "Basic programming skills"],
        }
    
    def _llm_value_extraction(self, text: str, understanding: str,
                              concepts: list, theorems: list, tools: list):
        """Use LLM to extract the core useful value."""
        prompt = f"""Analyze this document and identify what is USEFUL - the core theory, algorithm, model, or idea that someone can actually BUILD or IMPLEMENT.

Document Summary:
{understanding[:1000] if understanding else 'Not available'}

Main Concepts:
{', '.join(concepts[:10]) if concepts else 'None identified'}

Document Content:
{text[:3000]}...

Your task is to identify the MAIN USEFUL OUTPUT of this paper. For example:
- "Attention is All You Need" paper -> Transformer architecture (useful for building language models)
- A paper on sorting -> A new sorting algorithm (useful for efficient data sorting)
- A paper on neural networks -> A specific neural network architecture (useful for ML tasks)

Return a JSON object with:
{{
    "name": "Name of the useful thing (e.g., Transformer, DOA Algorithm, etc.)",
    "type": "algorithm|model|architecture|framework|technique|method",
    "description": "What it is and what problem it solves",
    "why_useful": "Why this is valuable and what it can be used for",
    "key_principles": ["List of core principles or components that make it work"],
    "prerequisites": ["What knowledge/tools are needed to implement it"]
}}

Return only valid JSON.
"""
        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            try:
                useful_value = json.loads(content)
                return useful_value
            except json.JSONDecodeError:
                return self._fallback_value_extraction(text, understanding, concepts, theorems, tools)
        except Exception:
            return self._fallback_value_extraction(text, understanding, concepts, theorems, tools)


class ImplementationGuideAgent:
    """Agent for generating actionable steps to build/implement the useful thing."""

    def __init__(self, llm=None):
        """Initialize the implementation guide agent."""
        self.llm = llm

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate implementation guide with steps, tools, and resources."""
        document_text = state.get("document_text", "")
        useful_value = state.get("useful_value", {})
        tools = state.get("tools", [])
        theorems = state.get("theorems", [])
        
        if not self.llm:
            implementation_guide = self._fallback_implementation_guide(
                document_text, useful_value, tools, theorems
            )
        else:
            implementation_guide = self._llm_implementation_guide(
                document_text, useful_value, tools, theorems
            )
        
        return {
            "implementation_guide": implementation_guide,
        }
    
    def _fallback_implementation_guide(self, text: str, useful_value: dict,
                                        tools: list, theorems: list):
        """Generate implementation guide without LLM."""
        value_name = useful_value.get("name", "The Method") if useful_value else "The Method"
        value_type = useful_value.get("type", "algorithm") if useful_value else "algorithm"
        
        # Extract tool names for requirements
        required_tools = []
        for tool in tools[:5]:
            if isinstance(tool, dict):
                required_tools.append(tool.get("name", "Unknown tool"))
            else:
                required_tools.append(str(tool))
        
        # Generate basic implementation steps based on document structure
        steps = [
            {
                "step": 1,
                "title": "Understand the Core Concepts",
                "description": f"Study the fundamental principles behind {value_name}.",
                "details": "Review the key principles and prerequisites listed in this document."
            },
            {
                "step": 2,
                "title": "Set Up the Environment",
                "description": "Install required tools and dependencies.",
                "details": f"Required tools: {', '.join(required_tools) if required_tools else 'See Tools section'}"
            },
            {
                "step": 3,
                "title": "Implement Core Components",
                "description": f"Build the main components of {value_name}.",
                "details": "Follow the algorithm/architecture description in this document."
            },
            {
                "step": 4,
                "title": "Integrate and Test",
                "description": "Combine components and validate functionality.",
                "details": "Use the theorems and validation criteria from the original work."
            },
            {
                "step": 5,
                "title": "Optimize and Deploy",
                "description": "Refine implementation for production use.",
                "details": "Apply optimizations mentioned in the results section."
            }
        ]
        
        return {
            "target": value_name,
            "target_type": value_type,
            "estimated_complexity": "Medium",
            "steps": steps,
            "required_tools": required_tools if required_tools else ["Programming language of choice"],
            "external_resources": [
                "Original paper/document for detailed specifications",
                "Related implementations for reference"
            ],
            "validation_criteria": [
                "Implementation matches described behavior",
                "Performance meets documented benchmarks"
            ]
        }
    
    def _llm_implementation_guide(self, text: str, useful_value: dict,
                                   tools: list, theorems: list):
        """Use LLM to generate implementation guide."""
        value_name = useful_value.get("name", "The Method") if useful_value else "The Method"
        value_type = useful_value.get("type", "algorithm") if useful_value else "algorithm"
        value_desc = useful_value.get("description", "") if useful_value else ""
        key_principles = useful_value.get("key_principles", []) if useful_value else []
        
        tools_desc = ", ".join([t.get("name", str(t)) if isinstance(t, dict) else str(t) 
                               for t in tools[:5]]) if tools else "None specified"
        
        prompt = f"""Generate a practical implementation guide for building "{value_name}" ({value_type}).

What it is:
{value_desc}

Key Principles:
{', '.join(key_principles) if key_principles else 'See document'}

Available Tools from Document:
{tools_desc}

Document Content:
{text[:2500]}...

Create a step-by-step guide that someone could follow to BUILD and IMPLEMENT this {value_type}. 
This should be ACTIONABLE - not just a summary, but actual steps to create it.

Return a JSON object with:
{{
    "target": "What you're building",
    "target_type": "algorithm|model|architecture|framework|technique",
    "estimated_complexity": "Low|Medium|High",
    "steps": [
        {{
            "step": 1,
            "title": "Step title",
            "description": "Brief description",
            "details": "Detailed instructions"
        }}
    ],
    "required_tools": ["List of tools/libraries needed"],
    "external_resources": ["Links or references to helpful resources"],
    "validation_criteria": ["How to verify the implementation works"]
}}

Return only valid JSON.
"""
        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            try:
                implementation_guide = json.loads(content)
                return implementation_guide
            except json.JSONDecodeError:
                return self._fallback_implementation_guide(text, useful_value, tools, theorems)
        except Exception:
            return self._fallback_implementation_guide(text, useful_value, tools, theorems)
