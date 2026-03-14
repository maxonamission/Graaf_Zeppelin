"""
Core KnowledgeGraph class for managing knowledge graphs in JSON format.
"""

import json
from typing import Dict, List, Any, Optional


class KnowledgeGraph:
    """
    A knowledge graph representation with nodes and edges.
    
    The JSON format is:
    {
        "nodes": [
            {"id": "node1", "label": "Node 1", "properties": {...}},
            ...
        ],
        "edges": [
            {"source": "node1", "target": "node2", "label": "relation", "properties": {...}},
            ...
        ]
    }
    """
    
    def __init__(self):
        self.nodes: List[Dict[str, Any]] = []
        self.edges: List[Dict[str, Any]] = []
    
    def add_node(self, node_id: str, label: str = "", properties: Optional[Dict[str, Any]] = None):
        """Add a node to the knowledge graph."""
        node = {
            "id": node_id,
            "label": label or node_id,
        }
        if properties:
            node["properties"] = properties
        self.nodes.append(node)
    
    def add_edge(self, source: str, target: str, label: str = "", properties: Optional[Dict[str, Any]] = None):
        """Add an edge to the knowledge graph."""
        edge = {
            "source": source,
            "target": target,
            "label": label,
        }
        if properties:
            edge["properties"] = properties
        self.edges.append(edge)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the knowledge graph to a dictionary."""
        return {
            "nodes": self.nodes,
            "edges": self.edges,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeGraph":
        """
        Create a knowledge graph from a dictionary.

        Performs basic schema validation: checks that the input is a dict,
        that 'nodes' and 'edges' are lists (if present), and that each node
        has an 'id' field and each edge has 'source' and 'target' fields.
        Raises ValueError if validation fails.
        """
        if not isinstance(data, dict):
            raise ValueError(f"Expected a dictionary, got {type(data).__name__}")

        nodes = data.get("nodes", [])
        edges = data.get("edges", [])

        if not isinstance(nodes, list):
            raise ValueError(f"Expected 'nodes' to be a list, got {type(nodes).__name__}")
        if not isinstance(edges, list):
            raise ValueError(f"Expected 'edges' to be a list, got {type(edges).__name__}")

        for i, node in enumerate(nodes):
            if not isinstance(node, dict):
                raise ValueError(f"Node at index {i} is not a dictionary")
            if "id" not in node:
                raise ValueError(f"Node at index {i} is missing required field 'id'")

        for i, edge in enumerate(edges):
            if not isinstance(edge, dict):
                raise ValueError(f"Edge at index {i} is not a dictionary")
            if "source" not in edge:
                raise ValueError(f"Edge at index {i} is missing required field 'source'")
            if "target" not in edge:
                raise ValueError(f"Edge at index {i} is missing required field 'target'")

        kg = cls()
        kg.nodes = nodes
        kg.edges = edges
        return kg
    
    def to_json(self, filepath: str, indent: int = 2):
        """Save the knowledge graph to a JSON file with UTF-8 encoding."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=indent, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, filepath: str) -> "KnowledgeGraph":
        """Load a knowledge graph from a JSON file with UTF-8 encoding."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def __repr__(self):
        return f"KnowledgeGraph(nodes={len(self.nodes)}, edges={len(self.edges)})"
