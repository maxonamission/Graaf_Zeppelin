"""
Graaf Zeppelin - Knowledge Graph Conversion Tool

A Python library for converting knowledge graphs between JSON, GEXF, and Markdown formats.
Supports UTF-8 encoding for all document formats.
"""

__version__ = "0.1.0"
__author__ = "Graaf Zeppelin Contributors"

from .converters import json_to_gexf, gexf_to_json, json_to_markdown, markdown_to_json
from .knowledge_graph import KnowledgeGraph

__all__ = [
    "KnowledgeGraph",
    "json_to_gexf",
    "gexf_to_json", 
    "json_to_markdown",
    "markdown_to_json",
]
