# Graaf Zeppelin

Een Python tool voor het converteren van knowledge graphs tussen JSON, GEXF en Markdown formaten. Ondersteunt UTF-8 encoding voor alle documentformaten.

A Python tool for converting knowledge graphs between JSON, GEXF, and Markdown formats. Supports UTF-8 encoding for all document formats.

## Features

- 📊 **JSON Knowledge Graphs**: Beheer knowledge graphs in gestructureerd JSON formaat
- 🔄 **Format Conversie**: Converteer tussen JSON, GEXF en Markdown
- 📝 **UTF-8 Support**: Volledige ondersteuning voor UTF-8 encoding in alle formaten
- 🐍 **Python API**: Programmeerbare interface voor integratie in je projecten
- 💻 **CLI Tool**: Command-line interface voor snelle conversies

## Installatie

```bash
# Clone de repository
git clone https://github.com/maxonamission/Graaf_Zeppelin.git
cd Graaf_Zeppelin

# Installeer dependencies
pip install -r requirements.txt

# Installeer het package
pip install -e .
```

## Gebruik

### Command Line Interface

Converteer tussen verschillende formaten:

```bash
# JSON naar GEXF
python -m graaf_zeppelin.cli convert examples/knowledge_graph.json output.gexf

# JSON naar Markdown
python -m graaf_zeppelin.cli convert examples/knowledge_graph.json output.md

# GEXF naar JSON
python -m graaf_zeppelin.cli convert input.gexf output.json

# Markdown naar JSON
python -m graaf_zeppelin.cli convert input.md output.json
```

Of gebruik het geïnstalleerde command:

```bash
graaf-zeppelin convert examples/knowledge_graph.json output.gexf
```

### Python API

```python
from graaf_zeppelin import KnowledgeGraph, json_to_gexf, json_to_markdown

# Maak een knowledge graph
kg = KnowledgeGraph()
kg.add_node("python", "Python", {"type": "programming_language"})
kg.add_node("data_science", "Data Science", {"type": "field"})
kg.add_edge("python", "data_science", "used in")

# Sla op als JSON (UTF-8)
kg.to_json("my_graph.json")

# Laad van JSON
kg = KnowledgeGraph.from_json("my_graph.json")

# Converteer naar andere formaten
json_to_gexf("my_graph.json", "my_graph.gexf")
json_to_markdown("my_graph.json", "my_graph.md")
```

## JSON Formaat

Het JSON formaat voor knowledge graphs:

```json
{
  "nodes": [
    {
      "id": "node1",
      "label": "Node Label",
      "properties": {
        "key": "value"
      }
    }
  ],
  "edges": [
    {
      "source": "node1",
      "target": "node2",
      "label": "relation",
      "properties": {
        "key": "value"
      }
    }
  ]
}
```

## Ondersteunde Formaten

- **JSON**: Gestructureerd formaat voor knowledge graphs met nodes en edges
- **GEXF**: Graph Exchange XML Format, compatibel met Gephi en andere graph tools
- **Markdown**: Menselijk leesbare documentatie met UTF-8 ondersteuning

## Voorbeelden

Zie de `examples/` directory voor voorbeeldbestanden:
- `examples/knowledge_graph.json` - Voorbeeld JSON knowledge graph

## Ontwikkeling

```bash
# Run tests (indien aanwezig)
python -m pytest

# Installeer in development mode
pip install -e .
```

## Licentie

Zie LICENSE bestand voor details.

## Contributing

Bijdragen zijn welkom! Open een issue of pull request.
