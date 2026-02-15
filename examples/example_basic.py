"""
Basis voorbeeld van het Graaf Zeppelin framework

Dit voorbeeld demonstreert het basisgebruik voor een kleine sportvereniging.
"""

import sys
sys.path.insert(0, '../src')

from graaf_zeppelin import (
    RelationshipGraph,
    AffectiveMetrics,
    DiagnosticTools,
    InterventionStrategies
)


def create_example_vereniging():
    """Maak een voorbeeld vereniging met leden en relaties."""
    
    # Initialiseer de graaf
    graph = RelationshipGraph()
    graph.set_metadata(
        naam_vereniging="Voetbalvereniging De Eendracht",
        datum_analyse="2026-02-15",
        beschrijving="Lokale voetbalvereniging met 15 leden"
    )
    
    # Voeg leden toe met attributen
    leden = [
        ("lid_001", "Jan de Vries", "speler", 25, 8.0),
        ("lid_002", "Sara Bakker", "coach", 35, 7.5),
        ("lid_003", "Tim Jansen", "speler", 22, 4.0),  # Laag welzijn
        ("lid_004", "Emma Visser", "speler", 24, 8.5),
        ("lid_005", "Luuk Peters", "vrijwilliger", 45, 7.0),
        ("lid_006", "Sophie Mulder", "speler", 23, 6.5),
        ("lid_007", "Daan van Dijk", "speler", 26, 7.5),
        ("lid_008", "Lisa de Jong", "coach", 32, 8.0),
        ("lid_009", "Max Smit", "speler", 21, 3.5),  # Laag welzijn
        ("lid_010", "Anna de Groot", "speler", 25, 7.5),
        ("lid_011", "Tom Bos", "vrijwilliger", 50, 7.0),
        ("lid_012", "Julia Vos", "speler", 24, 8.0),
        ("lid_013", "Thijs Meijer", "bestuurslid", 40, 6.5),
        ("lid_014", "Nina Hendriks", "speler", 22, 5.0),  # Gemiddeld welzijn
        ("lid_015", "Lars Schouten", "speler", 27, 8.5),
    ]
    
    for lid_id, naam, rol, leeftijd, welzijn in leden:
        graph.add_member(
            lid_id,
            naam=naam,
            rol=rol,
            leeftijd=leeftijd,
            emotionele_welzijn=welzijn
        )
    
    # Voeg relaties toe met affectieve kenmerken
    relaties = [
        # Sterke kern groep (Jan, Sara, Emma, Daan, Lisa, Anna, Lars)
        ("lid_001", "lid_002", 8.0, 9.0, 8.5, 8.0),  # Jan - Sara
        ("lid_001", "lid_004", 9.0, 8.5, 8.0, 8.5),  # Jan - Emma
        ("lid_001", "lid_007", 8.5, 8.0, 7.5, 8.0),  # Jan - Daan
        ("lid_002", "lid_004", 7.5, 8.0, 8.5, 8.0),  # Sara - Emma
        ("lid_002", "lid_008", 9.0, 9.5, 9.0, 9.0),  # Sara - Lisa (coaches)
        ("lid_004", "lid_007", 8.0, 7.5, 7.0, 7.5),  # Emma - Daan
        ("lid_004", "lid_010", 8.5, 8.0, 8.5, 8.0),  # Emma - Anna
        ("lid_007", "lid_015", 8.0, 8.5, 8.0, 8.5),  # Daan - Lars
        ("lid_008", "lid_010", 7.0, 7.5, 8.0, 7.5),  # Lisa - Anna
        ("lid_010", "lid_012", 8.5, 8.0, 8.5, 8.0),  # Anna - Julia
        ("lid_010", "lid_015", 8.0, 7.5, 7.0, 7.5),  # Anna - Lars
        ("lid_012", "lid_015", 7.5, 8.0, 7.5, 8.0),  # Julia - Lars
        
        # Zwakkere connecties met Tim (laag welzijn lid)
        ("lid_002", "lid_003", 6.0, 7.0, 6.5, 7.0),  # Sara - Tim
        ("lid_003", "lid_006", 5.5, 6.0, 5.5, 6.0),  # Tim - Sophie
        
        # Zwakkere connecties met Max (laag welzijn lid)
        ("lid_008", "lid_009", 5.0, 6.0, 5.5, 5.5),  # Lisa - Max
        
        # Sophie's connecties
        ("lid_006", "lid_014", 6.5, 7.0, 6.5, 7.0),  # Sophie - Nina
        ("lid_006", "lid_005", 6.0, 6.5, 6.0, 6.5),  # Sophie - Luuk
        
        # Vrijwilligers en bestuur
        ("lid_005", "lid_011", 7.5, 8.0, 7.5, 7.5),  # Luuk - Tom
        ("lid_005", "lid_013", 7.0, 7.5, 7.0, 7.0),  # Luuk - Thijs
        ("lid_011", "lid_013", 8.0, 8.5, 8.0, 8.0),  # Tom - Thijs
        ("lid_013", "lid_002", 7.5, 8.0, 7.5, 7.5),  # Thijs - Sara
        
        # Extra connecties
        ("lid_014", "lid_009", 5.5, 6.0, 5.5, 6.0),  # Nina - Max
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
    print("GRAAF ZEPPELIN - AFFECTIEVE DYNAMIEK ANALYSE")
    print("=" * 70)
    print()
    
    # Creëer voorbeeld vereniging
    print("⚽ Vereniging aanmaken...")
    graph = create_example_vereniging()
    metadata = graph.get_metadata()
    print(f"✓ {metadata['naam_vereniging']} geladen")
    print()
    
    # Basis netwerk statistieken
    print("-" * 70)
    print("📊 NETWERK STATISTIEKEN")
    print("-" * 70)
    stats = graph.get_graph_metrics()
    print(f"Aantal leden: {stats['aantal_leden']}")
    print(f"Aantal relaties: {stats['aantal_relaties']}")
    print(f"Gemiddeld aantal connecties per lid: {stats['gemiddelde_graad']:.1f}")
    print(f"Netwerk dichtheid: {stats['dichtheid']:.2f}")
    print(f"Gemiddelde clustering: {stats['gemiddelde_clustering']:.2f}")
    print(f"Volledig verbonden: {'Ja' if stats['is_verbonden'] else 'Nee'}")
    print()
    
    # Affectieve metrieken
    print("-" * 70)
    print("💚 AFFECTIEVE DIMENSIES")
    print("-" * 70)
    metrics = AffectiveMetrics(graph)
    
    # Emotioneel klimaat
    print("\n1. Emotioneel Klimaat:")
    emotional = metrics.calculate_emotional_climate()
    print(f"   Gemiddeld welzijn: {emotional['gemiddeld_welzijn']:.1f}/10")
    print(f"   Spreiding: {emotional['spreiding_welzijn']:.1f}")
    print(f"   Hoog welzijn (>7): {emotional['percentage_hoog_welzijn']:.0f}%")
    print(f"   Laag welzijn (<4): {emotional['percentage_laag_welzijn']:.0f}%")
    
    # Relationele kwaliteit
    print("\n2. Relationele Kwaliteit:")
    relational = metrics.calculate_relational_quality()
    print(f"   Gemiddelde relatie sterkte: {relational['gemiddelde_relatie_sterkte']:.1f}/10")
    print(f"   Gemiddeld vertrouwen: {relational['gemiddeld_vertrouwen']:.1f}/10")
    print(f"   Gemiddelde emotionele steun: {relational['gemiddelde_emotionele_steun']:.1f}/10")
    print(f"   Sterke relaties (>7): {relational['percentage_sterke_relaties']:.0f}%")
    
    # Psychologische veiligheid
    print("\n3. Psychologische Veiligheid:")
    safety = metrics.calculate_psychological_safety()
    print(f"   Gemiddelde veiligheid: {safety['gemiddelde_psychologische_veiligheid']:.1f}/10")
    print(f"   Hoge veiligheid (>7): {safety['percentage_hoge_veiligheid']:.0f}%")
    print(f"   Lage veiligheid (<4): {safety['percentage_lage_veiligheid']:.0f}%")
    
    # Culturele cohesie
    print("\n4. Culturele Cohesie:")
    cultural = metrics.calculate_cultural_cohesion()
    print(f"   Netwerk dichtheid: {cultural['netwerk_dichtheid']:.2f}")
    print(f"   Gemiddelde clustering: {cultural['gemiddelde_clustering']:.2f}")
    print(f"   Modulariteit: {cultural.get('modulariteit', 0):.2f}")
    print(f"   Fragmentatie: {cultural['fragmentatie']:.2f}")
    
    # Overall health
    print("\n5. Overall Affectieve Gezondheid:")
    comprehensive = metrics.calculate_comprehensive_score()
    print(f"   Emotioneel klimaat score: {comprehensive['emotioneel_klimaat_score']:.1f}/10")
    print(f"   Relationele kwaliteit score: {comprehensive['relationele_kwaliteit_score']:.1f}/10")
    print(f"   Psychologische veiligheid score: {comprehensive['psychologische_veiligheid_score']:.1f}/10")
    print(f"   Culturele cohesie score: {comprehensive['culturele_cohesie_score']:.1f}/10")
    print(f"   → TOTALE GEZONDHEID: {comprehensive['totale_affectieve_gezondheid']:.1f}/10")
    print()
    
    # Risico analyse
    print("-" * 70)
    print("⚠️  RISICO ANALYSE")
    print("-" * 70)
    risks = metrics.calculate_dropout_risk_indicators()
    print(f"\nTotaal aantal leden met verhoogd uitvalrisico: {risks['totaal_risico_leden']}")
    
    if risks['leden_met_laag_welzijn']:
        print(f"\nLeden met laag welzijn ({len(risks['leden_met_laag_welzijn'])}):")
        for lid_id in risks['leden_met_laag_welzijn']:
            attrs = graph.get_member_attributes(lid_id)
            print(f"   - {attrs['naam']} ({attrs['rol']}): welzijn {attrs['emotionele_welzijn']:.1f}/10")
    
    if risks['geisoleerde_leden']:
        print(f"\nGeïsoleerde leden ({len(risks['geisoleerde_leden'])}):")
        for lid_id in risks['geisoleerde_leden']:
            attrs = graph.get_member_attributes(lid_id)
            connecties = len(graph.get_neighbors(lid_id))
            print(f"   - {attrs['naam']} ({attrs['rol']}): {connecties} connecties")
    
    if risks['leden_met_zwakke_relaties']:
        print(f"\nLeden met alleen zwakke relaties ({len(risks['leden_met_zwakke_relaties'])}):")
        for lid_id in risks['leden_met_zwakke_relaties']:
            attrs = graph.get_member_attributes(lid_id)
            print(f"   - {attrs['naam']} ({attrs['rol']})")
    print()
    
    # Diagnostisch rapport
    print("-" * 70)
    print("🔍 DIAGNOSTISCH RAPPORT")
    print("-" * 70)
    diagnostics = DiagnosticTools(graph, metrics)
    report = diagnostics.generate_comprehensive_report()
    
    # Communities
    print("\nGedetecteerde communities:")
    for idx, community in enumerate(report['risico_analyse']['communities'], 1):
        print(f"\n   Community {idx} ({len(community)} leden):")
        for lid_id in community[:5]:  # Toon eerste 5
            attrs = graph.get_member_attributes(lid_id)
            print(f"      - {attrs['naam']}")
        if len(community) > 5:
            print(f"      ... en {len(community) - 5} anderen")
    
    # Key connectors
    print("\nBelangrijkste sociale knooppunten (top 5):")
    key_connectors = diagnostics.identify_key_connectors(top_n=5)
    for idx, connector in enumerate(key_connectors, 1):
        print(f"   {idx}. {connector['naam']} ({connector['rol']})")
        print(f"      Connecties: {connector['aantal_connecties']}, Score: {connector['connector_score']:.2f}")
    print()
    
    # Interventies
    print("-" * 70)
    print("💡 AANBEVOLEN INTERVENTIES")
    print("-" * 70)
    
    if report['prioritaire_interventies']:
        for idx, interventie in enumerate(report['prioritaire_interventies'], 1):
            print(f"\n{idx}. [{interventie['prioriteit']}] {interventie['dimensie']}")
            print(f"   Probleem: {interventie['probleem']}")
            print(f"   Aanbeveling: {interventie['aanbeveling']}")
            if interventie.get('betrokken_leden'):
                print(f"   Betrokken leden: {len(interventie['betrokken_leden'])}")
    else:
        print("\n✓ Geen urgente interventies nodig - vereniging is in goede staat!")
    print()
    
    # Buddy suggesties
    print("-" * 70)
    print("👥 BUDDY-SYSTEEM SUGGESTIES")
    print("-" * 70)
    interventions = InterventionStrategies(graph)
    buddy_pairs = interventions.suggest_buddy_pairs()
    
    if buddy_pairs:
        print(f"\nVoorgestelde buddy-paren ({len(buddy_pairs)}):\n")
        for pair in buddy_pairs:
            print(f"   {pair['geisoleerd_lid']['naam']} ← → {pair['voorgestelde_buddy']['naam']}")
            print(f"   {pair['rationale']}")
            print()
    else:
        print("\n✓ Geen geïsoleerde leden gevonden - buddy-systeem niet nodig")
    
    # Actieplan
    print("-" * 70)
    print("📅 ACTIEPLAN (12 WEKEN)")
    print("-" * 70)
    action_plan = interventions.create_action_plan(
        report['prioritaire_interventies'],
        timeline_weeks=12
    )
    
    for fase in action_plan['fasen']:
        print(f"\n{fase['periode']} - {fase['focus']}:")
        for actie in fase['acties']:
            print(f"   • {actie['actie']}")
            if actie.get('betrokkenen'):
                print(f"     (Betrokken: {len(actie['betrokkenen'])} leden)")
    
    print("\n\nMeetmomenten:")
    for meetmoment in action_plan['meetmomenten']:
        print(f"   Week {meetmoment['week']}: {meetmoment['type']}")
    
    print()
    print("=" * 70)
    print("✓ Analyse compleet!")
    print("=" * 70)


if __name__ == "__main__":
    main()
