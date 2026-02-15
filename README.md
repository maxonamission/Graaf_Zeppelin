# Graaf Zeppelin 🎈

## Framework voor Affectieve Dynamiek in Sportverenigingen

Een theoretisch onderbouwd en praktisch toepasbaar raamwerk waarmee sportverenigingen de **affectieve dynamiek** — het emotionele, relationele en culturele klimaat — binnen hun organisatie systematisch kunnen diagnosticeren en versterken.

### 🎯 Doelstellingen

- **Bevorderen van duurzame sportdeelname** door focus op emotioneel welzijn
- **Verminderen van uitval** door vroegtijdige identificatie van risicofactoren
- **Vergroten van psychologische veiligheid** binnen teams en verenigingen
- **Versterken van sociale cohesie** door inzicht in relatiepatronen

### 🧠 Theoretische Basis

Het framework is gebaseerd op:
- **Graaftheorie** voor modellering van sociale netwerken
- **Affectieve wetenschappen** voor emotionele dynamiek
- **Sociale netwerkanalyse** voor relatiepatronen
- **Organisatiepsychologie** voor interventiestrategieën

### ✨ Kernfunctionaliteit

#### 1. Relatiemodellering
Gebruik graaftheorie om het sociale netwerk binnen de vereniging te modelleren:
- Leden als nodes (met attributen zoals emotioneel welzijn, rol, leeftijd)
- Relaties als edges (met kenmerken zoals vertrouwen, sterkte, psychologische veiligheid)

#### 2. Affectieve Metrieken
Kwantificeer vier dimensies van affectieve dynamiek:
- **Emotioneel Klimaat**: Welzijn, betrokkenheid, enthousiasme
- **Relationele Kwaliteit**: Vertrouwen, steun, verbondenheid
- **Psychologische Veiligheid**: Veiligheid om jezelf te zijn
- **Culturele Cohesie**: Samenhang, inclusie, gedeelde waarden

#### 3. Diagnostische Tools
Systematische analyse met:
- Identificatie van geïsoleerde leden
- Detectie van communities/subgroepen
- Uitvalrisico-analyse
- Key connector identificatie
- Individuele rapporten per lid

#### 4. Interventiestrategieën
Evidence-based aanbevelingen:
- Buddy-systeem voorstellen voor geïsoleerde leden
- Team-building activiteiten
- Actieplannen met tijdlijn
- Communicatiestrategieën

#### 5. Visualisaties
Inzichtelijke representaties:
- Sociale netwerk visualisaties
- Community structuren
- Uitgebreide dashboards met alle metrieken

## 🚀 Installatie

```bash
# Clone de repository
git clone https://github.com/maxonamission/Graaf_Zeppelin.git
cd Graaf_Zeppelin

# Installeer dependencies
pip install -r requirements.txt

# Of installeer het package
pip install -e .
```

### Vereisten
- Python 3.8+
- NetworkX voor graafanalyse
- NumPy voor berekeningen
- Matplotlib voor visualisaties
- Pandas voor data handling

## 📖 Gebruik

### Basis Voorbeeld

```python
from graaf_zeppelin import (
    RelationshipGraph, 
    AffectiveMetrics, 
    DiagnosticTools,
    InterventionStrategies
)

# 1. Maak een relatie graaf
graph = RelationshipGraph()
graph.set_metadata(naam_vereniging="SV Voorbeeld", datum_analyse="2026-02-15")

# 2. Voeg leden toe
graph.add_member("lid_001", naam="Jan", rol="speler", leeftijd=25, emotionele_welzijn=8.0)
graph.add_member("lid_002", naam="Sara", rol="coach", leeftijd=35, emotionele_welzijn=7.5)
graph.add_member("lid_003", naam="Tim", rol="speler", leeftijd=22, emotionele_welzijn=4.0)

# 3. Voeg relaties toe
graph.add_relationship(
    "lid_001", "lid_002",
    sterkte=8.0,
    vertrouwen=9.0,
    emotionele_steun=8.5,
    psychologische_veiligheid=8.0
)
graph.add_relationship(
    "lid_002", "lid_003",
    sterkte=6.0,
    vertrouwen=7.0,
    emotionele_steun=6.5,
    psychologische_veiligheid=7.0
)

# 4. Bereken affectieve metrieken
metrics = AffectiveMetrics(graph)
emotional_climate = metrics.calculate_emotional_climate()
print(f"Gemiddeld welzijn: {emotional_climate['gemiddeld_welzijn']:.1f}")

comprehensive_score = metrics.calculate_comprehensive_score()
print(f"Totale affectieve gezondheid: {comprehensive_score['totale_affectieve_gezondheid']:.1f}/10")

# 5. Genereer diagnostisch rapport
diagnostics = DiagnosticTools(graph, metrics)
report = diagnostics.generate_comprehensive_report()

# Print prioritaire interventies
for interventie in report['prioritaire_interventies']:
    print(f"\n{interventie['prioriteit']}: {interventie['probleem']}")
    print(f"Aanbeveling: {interventie['aanbeveling']}")

# 6. Genereer interventiestrategieën
interventions = InterventionStrategies(graph)
buddy_pairs = interventions.suggest_buddy_pairs()
action_plan = interventions.create_action_plan(report['prioritaire_interventies'])

# 7. Visualiseer het netwerk
from graaf_zeppelin.visualization.network_viz import NetworkVisualizer, MetricsVisualizer

network_viz = NetworkVisualizer(graph)
fig = network_viz.plot_network(color_by='emotionele_welzijn', save_path='netwerk.png')

metrics_viz = MetricsVisualizer(graph, metrics)
dashboard = metrics_viz.plot_comprehensive_dashboard(save_path='dashboard.png')
```

## 📊 Voorbeelden

Zie de `examples/` directory voor complete voorbeelden:
- `example_basic.py` - Basisgebruik met kleine vereniging
- `example_analysis.py` - Uitgebreide analyse met grotere dataset
- `example_visualization.py` - Alle visualisatie opties

## 🔬 Methodologie

### Graaftheorische Benadering

Het framework modelleert de vereniging als een **ongerichte, gewogen graaf**:
- **Nodes** = Leden (spelers, coaches, vrijwilligers, bestuurders)
- **Edges** = Relaties met affectieve kenmerken
- **Gewichten** = Sterkte/kwaliteit van relaties

### Affectieve Dimensies

#### 1. Emotioneel Klimaat
- Gemiddeld emotioneel welzijn
- Spreiding (ongelijkheid in welzijn)
- Percentage leden met hoog/laag welzijn

#### 2. Relationele Kwaliteit  
- Gemiddelde relatiesterkte
- Vertrouwensniveau
- Emotionele steun
- Percentage sterke relaties

#### 3. Psychologische Veiligheid
- Gemiddelde veiligheidsscore
- Distributie over het netwerk
- Risicorelaties

#### 4. Culturele Cohesie
- Netwerk dichtheid
- Clustering coëfficiënt
- Modulariteit (subgroepen)
- Fragmentatie

### Centraliteitsmetrieken

Het framework gebruikt diverse centraliteitsmetrieken om belangrijke leden te identificeren:
- **Degree centrality**: Aantal directe connecties
- **Betweenness centrality**: Positie tussen anderen
- **Closeness centrality**: Gemiddelde afstand tot anderen
- **Eigenvector centrality**: Kwaliteit van connecties

### Risico-indicatoren

Identificeert leden met verhoogd uitvalrisico:
- Laag emotioneel welzijn (< 4/10)
- Sociale isolatie (< 2 connecties)
- Alleen zwakke relaties (geen sterkte > 5)

## 🎯 Use Cases

### 1. Periodieke Health Check
Voer elk kwartaal een meting uit om trends te monitoren en vroegtijdig in te grijpen.

### 2. Onboarding Nieuwe Leden
Identificeer geschikte buddies en faciliteer integratie in bestaande communities.

### 3. Interventie-effectiviteit
Meet voor en na interventies om impact te evalueren.

### 4. Team Compositie
Optimaliseer team-indelingen op basis van relationele compatibiliteit.

### 5. Coach Training
Identificeer coaches met grote invloed (hoge centraliteit) voor gerichte training.

## 🤝 Bijdragen

Bijdragen zijn welkom! Zie `CONTRIBUTING.md` voor richtlijnen.

## 📄 Licentie

Dit project is gelicenseerd onder de MIT License - zie het `LICENSE` bestand voor details.

## 📚 Referenties

Het framework is geïnspireerd door onderzoek in:
- Sociale netwerkanalyse (Wasserman & Faust, 1994)
- Psychologische veiligheid (Edmondson, 1999)
- Affectieve dynamiek in teams (Barsade & Knight, 2015)
- Sportdeelname en uitval (Balish et al., 2014)

## 👥 Contact

Voor vragen, suggesties of samenwerkingen:
- GitHub Issues: [github.com/maxonamission/Graaf_Zeppelin/issues](https://github.com/maxonamission/Graaf_Zeppelin/issues)

---

**Graaf Zeppelin** - Omdat duurzame sportdeelname begint met sterke sociale verbindingen 🎈🏃‍♀️⚽
