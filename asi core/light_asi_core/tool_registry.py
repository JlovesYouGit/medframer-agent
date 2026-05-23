from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional

from .config import RuntimeConfig
from .discovery_agent import DiscoveryAgent
from .node_mesh import NodeMeshStore
from .pattern_engine import RecursivePatternEngine


class ToolRegistry:
    """Registry of tools that the Ollama model can call during discovery."""

    def __init__(self, config: Optional[RuntimeConfig] = None) -> None:
        self.config = config or RuntimeConfig()
        self.tools: Dict[str, Callable] = {}
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Register default discovery tools."""
        self.register_tool("search_patterns", self._search_patterns_tool)
        self.register_tool("get_document_context", self._get_document_context_tool)
        self.register_tool("find_related_terms", self._find_related_terms_tool)
        self.register_tool("query_node_mesh", self._query_node_mesh_tool)

    def register_tool(self, name: str, func: Callable) -> None:
        """Register a tool function."""
        self.tools[name] = func

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions for model context."""
        definitions = []
        for name, func in self.tools.items():
            doc = func.__doc__ or f"Tool: {name}"
            definitions.append(
                {
                    "name": name,
                    "description": doc,
                    "parameters": {"type": "object", "properties": {}},
                }
            )
        return definitions

    def execute_tool(self, name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by name."""
        if name not in self.tools:
            return {"error": f"Tool '{name}' not found", "success": False}
        try:
            result = self.tools[name](**parameters)
            return {"result": result, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}

    def _search_patterns_tool(
        self, query: str, max_results: int = 10
    ) -> Dict[str, Any]:
        """Search for patterns matching the query."""
        pattern_engine = RecursivePatternEngine()
        # This would need access to current patterns
        # For now, return a placeholder
        return {
            "query": query,
            "matches": [],
            "message": "Pattern search requires current pattern context",
        }

    def _get_document_context_tool(
        self, endpoint_url: str, max_chars: int = 500
    ) -> Dict[str, Any]:
        """Get context from a specific document endpoint."""
        # This would need access to document store
        return {
            "endpoint_url": endpoint_url,
            "context": "",
            "message": "Document context requires document store access",
        }

    def _find_related_terms_tool(self, term: str, max_related: int = 5) -> Dict[str, Any]:
        """Find terms related to the given term."""
        mesh_store = NodeMeshStore(self.config.mesh_store_path)
        # Search node mesh for related terms
        term_id = f"term:{term}"
        if term_id in mesh_store.data["nodes"]:
            related = []
            for edge_id, edge in mesh_store.data["edges"].items():
                if edge["source"] == term_id and edge["kind"] == "co_occurs":
                    target_id = edge["target"]
                    if target_id in mesh_store.data["nodes"]:
                        related.append(
                            {
                                "term": mesh_store.data["nodes"][target_id].get("label", target_id),
                                "weight": edge.get("weight", 0),
                            }
                        )
            related.sort(key=lambda x: x["weight"], reverse=True)
            return {"term": term, "related": related[:max_related]}
        return {"term": term, "related": []}

    def _query_node_mesh_tool(
        self, query_type: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query the node mesh for various information."""
        mesh_store = NodeMeshStore(self.config.mesh_store_path)
        params = params or {}

        if query_type == "stats":
            return mesh_store.data.get("metadata", {})
        elif query_type == "nodes":
            return {"count": len(mesh_store.data.get("nodes", {}))}
        elif query_type == "edges":
            return {"count": len(mesh_store.data.get("edges", {}))}
        else:
            return {"error": f"Unknown query type: {query_type}"}


class ToolCallingDiscoveryAgent(DiscoveryAgent):
    """Extended discovery agent with tool-calling capabilities."""

    def __init__(self, config: Optional[RuntimeConfig] = None) -> None:
        super().__init__(config)
        self.tool_registry = ToolRegistry(config)

    def _build_tool_enhanced_prompt(
        self, query: str, documents, patterns
    ) -> str:
        """Build prompt with tool definitions available."""
        tool_definitions = self.tool_registry.get_tool_definitions()

        base_prompt = self._build_prompt(query, documents, patterns)

        tools_section = "\n\nAVAILABLE TOOLS:\n"
        for tool_def in tool_definitions:
            tools_section += f"- {tool_def['name']}: {tool_def['description']}\n"

        tools_section += (
            "\nYou can use these tools by including tool calls in your response "
            "in the format: TOOL_CALL(tool_name, {parameters})."
        )

        return base_prompt + tools_section

    def run_discovery_with_tools(
        self, query: str, model: str, medframework_root=None, max_files=None
    ):
        """Run discovery with tool-calling enabled."""
        # First, get initial discovery
        snapshot = self.index_medframework(medframework_root=medframework_root, max_files=max_files)
        documents = snapshot["documents"]
        patterns = snapshot["patterns"]

        # Build tool-enhanced prompt
        prompt = self._build_tool_enhanced_prompt(query, documents, patterns)

        # Get response from model
        response = self.ollama.chat(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a biomedical discovery assistant with access to analysis tools. Use tools when needed to enhance your analysis.",
                },
                {"role": "user", "content": prompt},
            ],
            options={"temperature": 0.2},
        )

        content = response.get("message", {}).get("content", "")

        # Parse and execute tool calls if present
        tool_results = []
        if "TOOL_CALL(" in content:
            tool_results = self._process_tool_calls(content)

        # If tools were called, get follow-up response
        if tool_results:
            followup_prompt = f"{prompt}\n\nTool Results:\n{json.dumps(tool_results, indent=2)}\n\nPlease provide your final analysis incorporating these tool results."
            response = self.ollama.chat(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a biomedical discovery assistant."},
                    {"role": "user", "content": followup_prompt},
                ],
                options={"temperature": 0.2},
            )
            content = response.get("message", {}).get("content", "")

        # Process final response
        from .utils import extract_json_object
        decoded = extract_json_object(content)
        if decoded is None:
            decoded = {
                "working_result": {
                    "result_type": "analysis",
                    "title": "Tool-enhanced discovery",
                    "content": content,
                    "assumptions": [],
                    "validation_steps": ["Review tool results for accuracy"],
                    "limitations": ["Tool-calling response parsing"],
                },
                "optimal_discovery_process": [],
                "explanation": {"summary": "Analysis with tool integration", "mechanistic_rationale": []},
                "evidence_endpoints": [doc.endpoint_url for doc in documents[:8]],
            }

        payload = self._normalize_payload(
            query=query, model=model, model_payload=decoded, patterns=patterns, documents=documents
        )
        payload["tool_calls_made"] = len(tool_results)
        payload["tool_results"] = tool_results

        from .types import DiscoveryResult
        return DiscoveryResult(query=query, model=model, payload=payload)

    def _process_tool_calls(self, content: str) -> List[Dict[str, Any]]:
        """Parse and execute tool calls from model response."""
        import re
        tool_pattern = r"TOOL_CALL\((\w+),\s*(\{.*?\})\)"
        matches = re.findall(tool_pattern, content, re.DOTALL)

        results = []
        for tool_name, params_str in matches:
            try:
                params = json.loads(params_str)
                result = self.tool_registry.execute_tool(tool_name, params)
                results.append({"tool": tool_name, "params": params, "result": result})
            except (json.JSONDecodeError, Exception) as e:
                results.append({"tool": tool_name, "error": str(e), "success": False})

        return results
