"""
Visualisatie voorbeeld van het Graaf Zeppelin framework

Dit voorbeeld demonstreert de visualisatie mogelijkheden.
"""

import sys
sys.path.insert(0, '../src')

from graaf_zeppelin import (
    RelationshipGraph,
    AffectiveMetrics,
)
from graaf_zeppelin.visualization.network_viz import (
    NetworkVisualizer,
    MetricsVisualizer
)


def create_example_vereniging():
    """Maak een voorbeeld vereniging met leden en relaties."""
    graph = RelationshipGraph()
    graph.set_metadata(
        naam_vereniging="SV Voorbeeldclub",
        datum_analyse="2026-02-15"
    )
    
    # Voeg leden toe
    leden = [
        ("lid_001", "Jan", "speler", 25, 8.0),
        ("lid_002", "Sara", "coach", 35, 7.5),
        ("lid_003", "Tim", "speler", 22, 4.0),
        ("lid_004", "Emma", "speler", 24, 8.5),
        ("lid_005", "Luuk", "vrijwilliger", 45, 7.0),
        ("lid_006", "Sophie", "speler", 23, 6.5),
        ("lid_007", "Daan", "speler", 26, 7.5),
        ("lid_008", "Lisa", "coach", 32, 8.0),
    ]
    
    for lid_id, naam, rol, leeftijd, welzijn in leden:
        graph.add_member(
            lid_id,
            naam=naam,
            rol=rol,
            leeftijd=leeftijd,
            emotionele_welzijn=welzijn
        )
    
    # Voeg relaties toe
    relaties = [
        ("lid_001", "lid_002", 8.0, 9.0, 8.5, 8.0),
        ("lid_001", "lid_004", 9.0, 8.5, 8.0, 8.5),
        ("lid_001", "lid_007", 8.5, 8.0, 7.5, 8.0),
        ("lid_002", "lid_004", 7.5, 8.0, 8.5, 8.0),
        ("lid_002", "lid_008", 9.0, 9.5, 9.0, 9.0),
        ("lid_002", "lid_003", 6.0, 7.0, 6.5, 7.0),
        ("lid_004", "lid_007", 8.0, 7.5, 7.0, 7.5),
        ("lid_005", "lid_006", 6.5, 7.0, 6.5, 7.0),
        ("lid_006", "lid_003", 5.5, 6.0, 5.5, 6.0),
    ]
    
    for lid1, lid2, sterkte, vertrouwen, steun, veiligheid in relaties:
        graph.add_relationship(
            lid1, lid2,
            sterkte=sterkte,
            vertrouwen=vertrouwen,
            emotionele_steun=steun,
            psychologische_veiligheid=veiligheid
        )
    
    return graph


def main():
    print("=" * 70)
    print("GRAAF ZEPPELIN - VISUALISATIE DEMONSTRATIE")
    print("=" * 70)
    print()
    
    # Creëer vereniging
    print("⚽ Vereniging aanmaken...")
    graph = create_example_vereniging()
    print("✓ Vereniging geladen")
    print()
    
    # Bereken metrics
    metrics = AffectiveMetrics(graph)
    
    # Visualisatie 1: Netwerk met emotioneel welzijn
    print("📊 Visualisatie 1: Netwerk gekleurd op emotioneel welzijn...")
    network_viz = NetworkVisualizer(graph)
    try:
        fig1 = network_viz.plot_network(
            color_by='emotionele_welzijn',
            size_by='centrality',
            layout='spring',
            save_path='netwerk_welzijn.png'
        )
        print("✓ Opgeslagen als: netwerk_welzijn.png")
    except Exception as e:
        print(f"⚠ Visualisatie niet mogelijk (matplotlib backend issue): {e}")
    print()
    
    # Visualisatie 2: Communities
    print("📊 Visualisatie 2: Gedetecteerde communities...")
    try:
        fig2 = network_viz.plot_communities(
            save_path='netwerk_communities.png'
        )
        print("✓ Opgeslagen als: netwerk_communities.png")
    except Exception as e:
        print(f"⚠ Visualisatie niet mogelijk (matplotlib backend issue): {e}")
    print()
    
    # Visualisatie 3: Comprehensive dashboard
    print("📊 Visualisatie 3: Uitgebreid dashboard...")
    metrics_viz = MetricsVisualizer(graph, metrics)
    try:
        fig3 = metrics_viz.plot_comprehensive_dashboard(
            save_path='dashboard_compleet.png'
        )
        print("✓ Opgeslagen als: dashboard_compleet.png")
    except Exception as e:
        print(f"⚠ Visualisatie niet mogelijk (matplotlib backend issue): {e}")
    print()
    
    # Toon metrics tekstueel
    print("=" * 70)
    print("METRIEKEN SAMENVATTING")
    print("=" * 70)
    
    comprehensive = metrics.calculate_comprehensive_score()
    print(f"\n✨ Totale Affectieve Gezondheid: {comprehensive['totale_affectieve_gezondheid']:.1f}/10")
    print(f"   - Emotioneel Klimaat: {comprehensive['emotioneel_klimaat_score']:.1f}/10")
    print(f"   - Relationele Kwaliteit: {comprehensive['relationele_kwaliteit_score']:.1f}/10")
    print(f"   - Psychologische Veiligheid: {comprehensive['psychologische_veiligheid_score']:.1f}/10")
    print(f"   - Culturele Cohesie: {comprehensive['culturele_cohesie_score']:.1f}/10")
    
    print()
    print("=" * 70)
    print("✓ Visualisatie demonstratie compleet!")
    print("=" * 70)
    print("\nOpmerking: Visualisaties kunnen alleen worden gegenereerd in een")
    print("omgeving met grafische mogelijkheden. In een headless omgeving")
    print("(zoals CI/CD) zijn visualisaties mogelijk niet beschikbaar.")


if __name__ == "__main__":
    main()
