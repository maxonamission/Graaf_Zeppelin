"""
Converters for knowledge graphs between JSON, GEXF, and Markdown formats.
All conversions support UTF-8 encoding.
"""

import json
import xml.etree.ElementTree as ET
from typing import Dict, Any
from .knowledge_graph import KnowledgeGraph


def json_to_gexf(json_filepath: str, gexf_filepath: str):
    """
    Convert a JSON knowledge graph to GEXF format.
    
    Args:
        json_filepath: Path to input JSON file
        gexf_filepath: Path to output GEXF file
    """
    kg = KnowledgeGraph.from_json(json_filepath)
    
    # Create GEXF XML structure
    gexf = ET.Element('gexf', {
        'xmlns': 'http://www.gexf.net/1.2draft',
        'version': '1.2'
    })
    
    graph = ET.SubElement(gexf, 'graph', {
        'mode': 'static',
        'defaultedgetype': 'directed'
    })
    
    # Add nodes
    nodes_elem = ET.SubElement(graph, 'nodes')
    for node in kg.nodes:
        node_attrs = {'id': node['id'], 'label': node.get('label', node['id'])}
        node_elem = ET.SubElement(nodes_elem, 'node', node_attrs)
        
        # Add properties as attvalues
        if 'properties' in node and node['properties']:
            attvalues = ET.SubElement(node_elem, 'attvalues')
            for key, value in node['properties'].items():
                ET.SubElement(attvalues, 'attvalue', {
                    'for': key,
                    'value': str(value)
                })
    
    # Add edges
    edges_elem = ET.SubElement(graph, 'edges')
    for idx, edge in enumerate(kg.edges):
        edge_attrs = {
            'id': str(idx),
            'source': edge['source'],
            'target': edge['target'],
        }
        if edge.get('label'):
            edge_attrs['label'] = edge['label']
        
        edge_elem = ET.SubElement(edges_elem, 'edge', edge_attrs)
        
        # Add properties as attvalues
        if 'properties' in edge and edge['properties']:
            attvalues = ET.SubElement(edge_elem, 'attvalues')
            for key, value in edge['properties'].items():
                ET.SubElement(attvalues, 'attvalue', {
                    'for': key,
                    'value': str(value)
                })
    
    # Write to file with UTF-8 encoding
    tree = ET.ElementTree(gexf)
    ET.indent(tree, space='  ')
    tree.write(gexf_filepath, encoding='utf-8', xml_declaration=True)


def gexf_to_json(gexf_filepath: str, json_filepath: str):
    """
    Convert a GEXF knowledge graph to JSON format.
    
    Args:
        gexf_filepath: Path to input GEXF file
        json_filepath: Path to output JSON file
    """
    # Parse GEXF file with UTF-8 encoding
    tree = ET.parse(gexf_filepath)
    root = tree.getroot()
    
    # Handle XML namespace
    ns = {'gexf': 'http://www.gexf.net/1.2draft'}
    
    kg = KnowledgeGraph()
    
    # Extract nodes
    nodes_elem = root.find('.//gexf:nodes', ns)
    if nodes_elem is None:
        nodes_elem = root.find('.//nodes')
    
    if nodes_elem is not None:
        for node in nodes_elem.findall('.//gexf:node', ns) or nodes_elem.findall('.//node'):
            node_id = node.get('id')
            label = node.get('label', node_id)
            
            properties = {}
            attvalues = node.find('.//gexf:attvalues', ns) or node.find('.//attvalues')
            if attvalues is not None:
                for attvalue in attvalues.findall('.//gexf:attvalue', ns) or attvalues.findall('.//attvalue'):
                    key = attvalue.get('for')
                    value = attvalue.get('value')
                    if key and value:
                        properties[key] = value
            
            kg.add_node(node_id, label, properties if properties else None)
    
    # Extract edges
    edges_elem = root.find('.//gexf:edges', ns)
    if edges_elem is None:
        edges_elem = root.find('.//edges')
    
    if edges_elem is not None:
        for edge in edges_elem.findall('.//gexf:edge', ns) or edges_elem.findall('.//edge'):
            source = edge.get('source')
            target = edge.get('target')
            label = edge.get('label', '')
            
            properties = {}
            attvalues = edge.find('.//gexf:attvalues', ns) or edge.find('.//attvalues')
            if attvalues is not None:
                for attvalue in attvalues.findall('.//gexf:attvalue', ns) or attvalues.findall('.//attvalue'):
                    key = attvalue.get('for')
                    value = attvalue.get('value')
                    if key and value:
                        properties[key] = value
            
            kg.add_edge(source, target, label, properties if properties else None)
    
    # Save to JSON with UTF-8 encoding
    kg.to_json(json_filepath)


def json_to_markdown(json_filepath: str, markdown_filepath: str):
    """
    Convert a JSON knowledge graph to Markdown format.
    
    Args:
        json_filepath: Path to input JSON file
        markdown_filepath: Path to output Markdown file
    """
    kg = KnowledgeGraph.from_json(json_filepath)
    
    lines = []
    lines.append("# Knowledge Graph\n")
    
    # Write nodes section
    lines.append("## Nodes\n")
    for node in kg.nodes:
        lines.append(f"### {node.get('label', node['id'])}\n")
        lines.append(f"- **ID**: {node['id']}\n")
        
        if 'properties' in node and node['properties']:
            lines.append("- **Properties**:\n")
            for key, value in node['properties'].items():
                lines.append(f"  - {key}: {value}\n")
        lines.append("\n")
    
    # Write edges section
    lines.append("## Edges\n")
    
    # Create node ID to label mapping for efficient lookup
    node_labels = {node['id']: node.get('label', node['id']) for node in kg.nodes}
    
    for edge in kg.edges:
        source_label = node_labels.get(edge['source'], edge['source'])
        target_label = node_labels.get(edge['target'], edge['target'])
        
        relation = edge.get('label', 'related to')
        lines.append(f"- **{source_label}** {relation} **{target_label}**\n")
        
        if 'properties' in edge and edge['properties']:
            for key, value in edge['properties'].items():
                lines.append(f"  - {key}: {value}\n")
    
    # Write to file with UTF-8 encoding
    with open(markdown_filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def markdown_to_json(markdown_filepath: str, json_filepath: str):
    """
    Convert a Markdown knowledge graph to JSON format.
    
    This is a simple parser that expects a specific Markdown format:
    - Nodes are defined as level 3 headers (###)
    - Edges are defined as list items with ** ** notation
    
    Args:
        markdown_filepath: Path to input Markdown file
        json_filepath: Path to output JSON file
    """
    kg = KnowledgeGraph()
    
    with open(markdown_filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    current_node_id = None
    current_node_label = None
    in_nodes_section = False
    in_edges_section = False
    
    for line in lines:
        line = line.rstrip()
        
        if line.startswith("## Nodes"):
            in_nodes_section = True
            in_edges_section = False
            continue
        elif line.startswith("## Edges"):
            in_nodes_section = False
            in_edges_section = True
            continue
        elif line.startswith("## "):
            in_nodes_section = False
            in_edges_section = False
            continue
        
        if in_nodes_section:
            if line.startswith("### "):
                # New node
                if current_node_id:
                    kg.add_node(current_node_id, current_node_label)
                
                current_node_label = line[4:].strip()
                current_node_id = current_node_label.lower().replace(" ", "_")
            elif line.startswith("- **ID**: "):
                current_node_id = line[10:].strip()
        
        elif in_edges_section:
            if line.startswith("- **") and "**" in line[4:]:
                # Parse edge: - **Source** relation **Target**
                parts = line[2:].split("**")
                if len(parts) >= 4:
                    source_label = parts[1].strip()
                    target_label = parts[3].strip()
                    
                    # Get the relation text between source and target
                    relation = parts[2].strip()
                    
                    # Convert labels to IDs (simplified)
                    source_id = source_label.lower().replace(" ", "_")
                    target_id = target_label.lower().replace(" ", "_")
                    
                    kg.add_edge(source_id, target_id, relation)
    
    # Add last node if exists
    if current_node_id:
        kg.add_node(current_node_id, current_node_label)
    
    # Save to JSON with UTF-8 encoding
    kg.to_json(json_filepath)
