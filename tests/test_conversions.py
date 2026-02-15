"""
Simple tests for Graaf Zeppelin knowledge graph conversions.
"""

import os
import json
import tempfile
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graaf_zeppelin import KnowledgeGraph, json_to_gexf, gexf_to_json, json_to_markdown, markdown_to_json

# Create a temporary directory for test files
TEST_DIR = tempfile.mkdtemp(prefix="graaf_zeppelin_test_")


def test_knowledge_graph_creation():
    """Test creating and manipulating a knowledge graph."""
    print("Testing KnowledgeGraph creation...")
    kg = KnowledgeGraph()
    
    # Add nodes
    kg.add_node("node1", "Node 1", {"type": "test"})
    kg.add_node("node2", "Node 2")
    
    # Add edges
    kg.add_edge("node1", "node2", "connects to")
    
    assert len(kg.nodes) == 2, "Should have 2 nodes"
    assert len(kg.edges) == 1, "Should have 1 edge"
    
    print("✓ KnowledgeGraph creation test passed")


def test_json_roundtrip():
    """Test saving and loading JSON."""
    print("Testing JSON roundtrip...")
    kg = KnowledgeGraph()
    kg.add_node("test", "Test Node", {"key": "value"})
    kg.add_edge("test", "test", "self-reference")
    
    # Save to JSON
    json_path = os.path.join(TEST_DIR, "test_kg.json")
    kg.to_json(json_path)
    
    # Load from JSON
    kg2 = KnowledgeGraph.from_json(json_path)
    
    assert len(kg2.nodes) == 1, "Should have 1 node after loading"
    assert len(kg2.edges) == 1, "Should have 1 edge after loading"
    assert kg2.nodes[0]["label"] == "Test Node", "Label should be preserved"
    
    print("✓ JSON roundtrip test passed")


def test_utf8_encoding():
    """Test UTF-8 encoding with special characters."""
    print("Testing UTF-8 encoding...")
    kg = KnowledgeGraph()
    kg.add_node("café", "Café ☕", {"description": "Een gezellige plek"})
    kg.add_node("über", "Über 🎵", {"description": "Muziek van Dvorák"})
    kg.add_edge("café", "über", "heeft", {"note": "éèêë"})
    
    # Save and load
    json_path = os.path.join(TEST_DIR, "test_utf8.json")
    kg.to_json(json_path)
    kg2 = KnowledgeGraph.from_json(json_path)
    
    assert kg2.nodes[0]["id"] == "café", "UTF-8 ID should be preserved"
    assert "☕" in kg2.nodes[0]["label"], "Emoji should be preserved"
    assert "Dvorák" in kg2.nodes[1]["properties"]["description"], "Accented characters should be preserved"
    
    print("✓ UTF-8 encoding test passed")


def test_json_to_gexf_conversion():
    """Test converting JSON to GEXF."""
    print("Testing JSON to GEXF conversion...")
    
    # Create test JSON
    kg = KnowledgeGraph()
    kg.add_node("n1", "Node 1")
    kg.add_node("n2", "Node 2")
    kg.add_edge("n1", "n2", "related to")
    
    json_path = os.path.join(TEST_DIR, "test_convert.json")
    gexf_path = os.path.join(TEST_DIR, "test_convert.gexf")
    
    kg.to_json(json_path)
    json_to_gexf(json_path, gexf_path)
    
    # Check GEXF file exists and contains expected content
    assert os.path.exists(gexf_path), "GEXF file should exist"
    with open(gexf_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'Node 1' in content, "Node label should be in GEXF"
        assert 'n1' in content, "Node ID should be in GEXF"
        assert 'related to' in content, "Edge label should be in GEXF"
    
    print("✓ JSON to GEXF conversion test passed")


def test_json_to_markdown_conversion():
    """Test converting JSON to Markdown."""
    print("Testing JSON to Markdown conversion...")
    
    kg = KnowledgeGraph()
    kg.add_node("python", "Python", {"type": "language"})
    kg.add_node("data", "Data Science")
    kg.add_edge("python", "data", "used in")
    
    json_path = os.path.join(TEST_DIR, "test_md.json")
    md_path = os.path.join(TEST_DIR, "test_md.md")
    
    kg.to_json(json_path)
    json_to_markdown(json_path, md_path)
    
    # Check Markdown file exists and contains expected content
    assert os.path.exists(md_path), "Markdown file should exist"
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert '# Knowledge Graph' in content, "Should have title"
        assert '## Nodes' in content, "Should have nodes section"
        assert '## Edges' in content, "Should have edges section"
        assert 'Python' in content, "Node label should be in Markdown"
        assert 'used in' in content, "Edge label should be in Markdown"
    
    print("✓ JSON to Markdown conversion test passed")


def test_gexf_to_json_conversion():
    """Test converting GEXF back to JSON."""
    print("Testing GEXF to JSON conversion...")
    
    # First create JSON and convert to GEXF
    kg = KnowledgeGraph()
    kg.add_node("a", "Node A", {"prop": "value"})
    kg.add_node("b", "Node B")
    kg.add_edge("a", "b", "links to")
    
    json_path1 = os.path.join(TEST_DIR, "test_gexf_src.json")
    gexf_path = os.path.join(TEST_DIR, "test_gexf_mid.gexf")
    json_path2 = os.path.join(TEST_DIR, "test_gexf_dst.json")
    
    kg.to_json(json_path1)
    json_to_gexf(json_path1, gexf_path)
    gexf_to_json(gexf_path, json_path2)
    
    # Load the result and verify
    kg2 = KnowledgeGraph.from_json(json_path2)
    assert len(kg2.nodes) == 2, "Should have 2 nodes after conversion"
    assert len(kg2.edges) == 1, "Should have 1 edge after conversion"
    assert kg2.nodes[0]["label"] == "Node A", "Node label should be preserved"
    
    print("✓ GEXF to JSON conversion test passed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Graaf Zeppelin Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_knowledge_graph_creation,
        test_json_roundtrip,
        test_utf8_encoding,
        test_json_to_gexf_conversion,
        test_json_to_markdown_conversion,
        test_gexf_to_json_conversion,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ Test failed: {test.__name__}")
            print(f"  Error: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    # Cleanup temporary directory
    import shutil
    try:
        shutil.rmtree(TEST_DIR)
        print(f"\n✓ Cleaned up temporary test directory")
    except Exception as e:
        print(f"\nWarning: Could not clean up test directory: {e}")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
