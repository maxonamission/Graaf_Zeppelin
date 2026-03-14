# Graaf Zeppelin - Documentatie / Documentation

## Overzicht / Overview

**Nederlands:**
Graaf Zeppelin is een Python library voor het converteren van knowledge graphs tussen verschillende formaten. Het ondersteunt JSON, GEXF (Graph Exchange XML Format) en Markdown, allemaal met volledige UTF-8 ondersteuning.

**English:**
Graaf Zeppelin is a Python library for converting knowledge graphs between different formats. It supports JSON, GEXF (Graph Exchange XML Format), and Markdown, all with full UTF-8 support.

## Installatie / Installation

```bash
# Clone de repository / Clone the repository
git clone https://github.com/maxonamission/Graaf_Zeppelin.git
cd Graaf_Zeppelin

# Installeer dependencies / Install dependencies
pip install -r requirements.txt

# Installeer het package / Install the package
pip install -e .
```

> **Opmerking over dependencies / Note on dependencies:**
> `requirements.txt` bevat naast de core dependencies (zoals `networkx`) ook packages voor web/API-uitbreidingen (zoals `fastapi`, `uvicorn`, `sqlalchemy`). Als je alleen de knowledge graph conversie-functies wilt gebruiken, volstaat `pip install -e .` — de core-functionaliteit heeft alleen de standaard Python-library nodig.
>
> `requirements.txt` includes web/API extension packages (such as `fastapi`, `uvicorn`, `sqlalchemy`) in addition to core dependencies (like `networkx`). If you only need the knowledge graph conversion functions, `pip install -e .` is sufficient — the core functionality only requires the Python standard library.

## Gebruik / Usage

### 1. Command Line Interface (CLI)

De eenvoudigste manier om knowledge graphs te converteren is via de command line:

The easiest way to convert knowledge graphs is via the command line:

```bash
# JSON → GEXF
graaf-zeppelin convert input.json output.gexf

# JSON → Markdown
graaf-zeppelin convert input.json output.md

# GEXF → JSON
graaf-zeppelin convert input.gexf output.json

# Markdown → JSON
graaf-zeppelin convert input.md output.json
```

Of gebruik de Python module direct:

Or use the Python module directly:

```bash
python -m graaf_zeppelin.cli convert input.json output.gexf
```

### 2. Python API

Voor meer controle kun je de Python API gebruiken:

For more control, you can use the Python API:

```python
from graaf_zeppelin import KnowledgeGraph

# Maak een nieuwe knowledge graph / Create a new knowledge graph
kg = KnowledgeGraph()

# Voeg nodes toe / Add nodes
kg.add_node("python", "Python", {
    "type": "programming_language",
    "paradigm": "multi-paradigm"
})

kg.add_node("data_science", "Data Science", {
    "type": "field"
})

# Voeg edges toe / Add edges
kg.add_edge("python", "data_science", "used in", {
    "strength": "strong"
})

# Sla op / Save
kg.to_json("my_graph.json")

# Laad / Load
kg2 = KnowledgeGraph.from_json("my_graph.json")
```

### 3. Format Conversie / Format Conversion

Gebruik de converter functies:

Use the converter functions:

```python
from graaf_zeppelin import json_to_gexf, json_to_markdown, gexf_to_json

# Converteer JSON naar GEXF / Convert JSON to GEXF
json_to_gexf("input.json", "output.gexf")

# Converteer JSON naar Markdown / Convert JSON to Markdown
json_to_markdown("input.json", "output.md")

# Converteer GEXF naar JSON / Convert GEXF to JSON
gexf_to_json("input.gexf", "output.json")
```

## JSON Formaat / JSON Format

Het JSON formaat is eenvoudig en krachtig:

The JSON format is simple and powerful:

```json
{
  "nodes": [
    {
      "id": "unique_id",
      "label": "Display Label",
      "properties": {
        "key1": "value1",
        "key2": "value2"
      }
    }
  ],
  "edges": [
    {
      "source": "node_id_1",
      "target": "node_id_2",
      "label": "relation_type",
      "properties": {
        "key1": "value1"
      }
    }
  ]
}
```

### Velden / Fields

**Nodes:**
- `id` (verplicht/required): Unieke identifier voor de node
- `label` (optioneel/optional): Menselijk leesbare naam (gebruikt id als label niet is opgegeven)
- `properties` (optioneel/optional): Dictionary met extra eigenschappen

**Edges:**
- `source` (verplicht/required): ID van de bron node
- `target` (verplicht/required): ID van de doel node
- `label` (optioneel/optional): Type relatie of beschrijving
- `properties` (optioneel/optional): Dictionary met extra eigenschappen

> **Validatie / Validation:**
> `KnowledgeGraph.from_dict()` en `KnowledgeGraph.from_json()` voeren basisvalidatie uit: ze controleren dat de invoer een dictionary is, dat `nodes` en `edges` lijsten zijn, dat elke node een `id` veld heeft, en dat elke edge `source` en `target` velden heeft. Bij ongeldige data wordt een `ValueError` gegenereerd. Er worden geen verdere type- of waarde-controles gedaan op optionele velden.
>
> `KnowledgeGraph.from_dict()` and `KnowledgeGraph.from_json()` perform basic schema validation: they check that the input is a dictionary, that `nodes` and `edges` are lists, that each node has an `id` field, and that each edge has `source` and `target` fields. A `ValueError` is raised for invalid data. No further type or value checks are performed on optional fields.

## UTF-8 Ondersteuning / UTF-8 Support

**Nederlands:**
Graaf Zeppelin heeft volledige UTF-8 ondersteuning. Je kunt veilig speciale karakters, emoji's en niet-Latijnse tekst gebruiken:

**English:**
Graaf Zeppelin has full UTF-8 support. You can safely use special characters, emojis, and non-Latin text:

```python
kg = KnowledgeGraph()
kg.add_node("café", "Café ☕", {"beschrijving": "Een gezellige plek"})
kg.add_node("über", "Über 🎵", {"componist": "Dvorák"})
kg.add_edge("café", "über", "speelt", {"tijdstip": "'s avonds"})
```

## Voorbeelden / Examples

### Voorbeeld 1: Eenvoudige Knowledge Graph

```python
from graaf_zeppelin import KnowledgeGraph

kg = KnowledgeGraph()

# Technologie ecosysteem
kg.add_node("python", "Python", {"type": "language"})
kg.add_node("django", "Django", {"type": "framework"})
kg.add_node("web", "Web Development", {"type": "domain"})

kg.add_edge("django", "python", "written in")
kg.add_edge("django", "web", "used for")

kg.to_json("tech_stack.json")
```

### Voorbeeld 2: Conversie Workflow

```python
from graaf_zeppelin import json_to_gexf, json_to_markdown

# Start met JSON
kg = KnowledgeGraph()
# ... voeg nodes en edges toe
kg.to_json("knowledge.json")

# Converteer naar GEXF voor visualisatie in Gephi
json_to_gexf("knowledge.json", "knowledge.gexf")

# Converteer naar Markdown voor documentatie
json_to_markdown("knowledge.json", "knowledge.md")
```

### Voorbeeld 3: CLI Gebruik

```bash
# Maak een knowledge graph in JSON
# Convert naar verschillende formaten
graaf-zeppelin convert data.json data.gexf
graaf-zeppelin convert data.json data.md

# Importeer van GEXF
graaf-zeppelin convert external.gexf internal.json
```

## Ondersteunde Formaten / Supported Formats

### JSON
- **Lezen/Read**: ✓
- **Schrijven/Write**: ✓
- **UTF-8**: ✓
- **Gebruik/Use**: Primair formaat voor data storage en uitwisseling

### GEXF (Graph Exchange XML Format)
- **Lezen/Read**: ✓
- **Schrijven/Write**: ✓
- **UTF-8**: ✓
- **Gebruik/Use**: Visualisatie in Gephi, Cytoscape en andere graph tools

> **Compatibiliteitsnota / Compatibility note:**
> Node- en edge-properties worden opgeslagen als `<attvalue for="key" value="value" />` elementen in het GEXF-bestand. Er worden geen `<attributes>`-definities op grafiekniveau gegenereerd. Bij het importeren van externe GEXF-bestanden worden alleen inline `attvalue`-elementen herkend.
>
> Node and edge properties are stored as `<attvalue for="key" value="value" />` elements in the GEXF file. No graph-level `<attributes>` definitions are generated. When importing external GEXF files, only inline `attvalue` elements are recognized.

### Markdown
- **Lezen/Read**: ✓ (beperkt/limited)
- **Schrijven/Write**: ✓
- **UTF-8**: ✓
- **Gebruik/Use**: Menselijk leesbare documentatie en rapportage

#### Verwacht Markdown-formaat / Expected Markdown Format

**Nederlands:**
De `markdown_to_json()` parser verwacht een specifiek Markdown-formaat. Nodes worden gedefinieerd als level-3 headers (`###`) met een `- **ID**: ...` regel en optioneel een `- **Properties**:` blok met geneste `- key: value` regels. Edges worden gedefinieerd als lijstitems in de vorm `- **BronLabel** relatie **DoelLabel**` met optionele geneste properties.

**English:**
The `markdown_to_json()` parser expects a specific Markdown format. Nodes are defined as level-3 headers (`###`) with a `- **ID**: ...` line and optionally a `- **Properties**:` block with nested `- key: value` lines. Edges are defined as list items in the form `- **SourceLabel** relation **TargetLabel**` with optional nested properties.

**Voorbeeld / Example:**

```markdown
# Knowledge Graph

## Nodes

### Python

- **ID**: python
- **Properties**:
  - type: language
  - paradigm: multi-paradigm

### Data Science

- **ID**: data_science

## Edges

- **Python** used in **Data Science**
  - strength: strong
```

## Testen / Testing

```bash
# Run de test suite / Run the test suite
python tests/test_conversions.py

# Of met pytest (indien geïnstalleerd)
# Or with pytest (if installed)
pytest tests/
```

## Veelgestelde Vragen / FAQ

**Q: Kan ik Unicode karakters gebruiken in node IDs?**  
**Q: Can I use Unicode characters in node IDs?**

A: Ja! Alle strings ondersteunen volledige UTF-8 encoding.  
A: Yes! All strings support full UTF-8 encoding.

**Q: Hoe kan ik mijn GEXF file uit Gephi importeren?**  
**Q: How can I import my GEXF file from Gephi?**

A: Gebruik `graaf-zeppelin convert myfile.gexf output.json` of de `gexf_to_json()` functie.  
A: Use `graaf-zeppelin convert myfile.gexf output.json` or the `gexf_to_json()` function.

**Q: Worden node/edge properties behouden bij conversie?**  
**Q: Are node/edge properties preserved during conversion?**

A: Ja, alle properties worden behouden bij conversie tussen JSON en GEXF. Markdown conversie is meer beperkt.  
A: Yes, all properties are preserved when converting between JSON and GEXF. Markdown conversion is more limited.

## Licentie / License

Zie LICENSE bestand / See LICENSE file

## Contributing

Bijdragen zijn welkom! Open een issue of pull request op GitHub.  
Contributions are welcome! Open an issue or pull request on GitHub.
