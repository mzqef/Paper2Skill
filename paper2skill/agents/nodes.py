"""Agent nodes for the multi-agent workflow."""

from typing import Dict, Any
import json


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
        # Simple keyword-based extraction
        concepts = []
        theorems = []
        results = []
        
        lines = text.split('\n')
        for line in lines:
            lower_line = line.lower()
            if any(keyword in lower_line for keyword in ['theorem', 'lemma', 'proposition']):
                theorems.append({
                    "name": line.strip()[:100],
                    "description": "Extracted from document",
                    "type": "theorem"
                })
            elif any(keyword in lower_line for keyword in ['result', 'finding', 'conclusion']):
                results.append({
                    "description": line.strip()[:200],
                    "type": "result"
                })
        
        # Extract general concepts from headings (lines that are short and in title case)
        for line in lines:
            stripped = line.strip()
            if len(line.split()) < 10 and stripped and not stripped.startswith('#'):
                if stripped and stripped[0].isupper():
                    concepts.append(stripped)
        
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
        
        # Common tool keywords
        tool_keywords = [
            'algorithm', 'method', 'technique', 'approach', 'framework',
            'model', 'system', 'tool', 'library', 'implementation'
        ]
        
        lines = text.split('\n')
        for line in lines:
            lower_line = line.lower()
            for keyword in tool_keywords:
                if keyword in lower_line:
                    tools.append({
                        "name": line.strip()[:100],
                        "description": f"Identified from context containing '{keyword}'",
                        "type": "tool/method"
                    })
                    break
        
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
