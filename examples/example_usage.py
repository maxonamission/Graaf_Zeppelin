#!/usr/bin/env python3
"""
Voorbeeld script voor het gebruik van Graaf Zeppelin.
Example script for using Graaf Zeppelin.

Dit script demonstreert:
- Het maken van een knowledge graph
- Het toevoegen van nodes en edges
- Het opslaan in JSON formaat
- Het converteren naar GEXF en Markdown

This script demonstrates:
- Creating a knowledge graph
- Adding nodes and edges
- Saving in JSON format
- Converting to GEXF and Markdown
"""

from graaf_zeppelin import KnowledgeGraph, json_to_gexf, json_to_markdown

def main():
    print("Graaf Zeppelin - Voorbeeld / Example")
    print("=" * 60)
    
    # Maak een nieuwe knowledge graph
    # Create a new knowledge graph
    print("\n1. Een knowledge graph maken / Creating a knowledge graph...")
    kg = KnowledgeGraph()
    
    # Voeg nodes toe met UTF-8 karakters
    # Add nodes with UTF-8 characters
    print("2. Nodes toevoegen / Adding nodes...")
    kg.add_node(
        "nederland",
        "Nederland 🇳🇱",
        {
            "type": "land",
            "hoofdstad": "Amsterdam",
            "inwoners": "17.5 miljoen"
        }
    )
    
    kg.add_node(
        "amsterdam",
        "Amsterdam",
        {
            "type": "stad",
            "provincie": "Noord-Holland"
        }
    )
    
    kg.add_node(
        "rotterdam",
        "Rotterdam",
        {
            "type": "stad",
            "provincie": "Zuid-Holland",
            "haven": "grootste van Europa"
        }
    )
    
    kg.add_node(
        "graaf_zeppelin",
        "Graaf Zeppelin ✈️",
        {
            "type": "luchtschip",
            "actief": "1928-1937"
        }
    )
    
    # Voeg relaties toe (edges)
    # Add relationships (edges)
    print("3. Edges toevoegen / Adding edges...")
    kg.add_edge(
        "nederland",
        "amsterdam",
        "heeft hoofdstad",
        {"sinds": "1814"}
    )
    
    kg.add_edge(
        "nederland",
        "rotterdam",
        "heeft stad"
    )
    
    kg.add_edge(
        "graaf_zeppelin",
        "amsterdam",
        "bezocht",
        {"jaar": "1931", "gebeurtenis": "vloot boven de stad"}
    )
    
    print(f"   → Knowledge graph aangemaakt met {len(kg.nodes)} nodes en {len(kg.edges)} edges")
    print(f"   → Knowledge graph created with {len(kg.nodes)} nodes and {len(kg.edges)} edges")
    
    # Sla op als JSON
    # Save as JSON
    print("\n4. Opslaan als JSON / Saving as JSON...")
    json_path = "output/example_graph.json"
    kg.to_json(json_path)
    print(f"   ✓ Opgeslagen / Saved: {json_path}")
    
    # Converteer naar GEXF
    # Convert to GEXF
    print("\n5. Converteren naar GEXF / Converting to GEXF...")
    gexf_path = "output/example_graph.gexf"
    json_to_gexf(json_path, gexf_path)
    print(f"   ✓ Geconverteerd / Converted: {gexf_path}")
    print("   → Kan geopend worden in Gephi en andere graph tools")
    print("   → Can be opened in Gephi and other graph tools")
    
    # Converteer naar Markdown
    # Convert to Markdown
    print("\n6. Converteren naar Markdown / Converting to Markdown...")
    md_path = "output/example_graph.md"
    json_to_markdown(json_path, md_path)
    print(f"   ✓ Geconverteerd / Converted: {md_path}")
    print("   → Menselijk leesbaar met UTF-8 ondersteuning")
    print("   → Human-readable with UTF-8 support")
    
    print("\n" + "=" * 60)
    print("✓ Klaar! Bekijk de bestanden in de output/ directory")
    print("✓ Done! Check the files in the output/ directory")
    print("=" * 60)
    
    # Toon een preview van de JSON
    # Show a preview of the JSON
    print("\nJSON voorbeeld / JSON preview:")
    print("-" * 60)
    import json
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(json.dumps(data, indent=2, ensure_ascii=False)[:500] + "...")

if __name__ == "__main__":
    import os
    os.makedirs("output", exist_ok=True)
    main()
