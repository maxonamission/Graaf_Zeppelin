"""
DiagnosticTools: Diagnostische tools voor affectieve dynamiek analyse

Dit module biedt tools om de affectieve dynamiek binnen een sportvereniging
te diagnosticeren en aanbevelingen te genereren.
"""

from typing import Dict, List, Any
from ..core.relationship_graph import RelationshipGraph
from ..core.affective_metrics import AffectiveMetrics


class DiagnosticTools:
    """
    Diagnostische tools voor systematische analyse van affectieve dynamiek.
    
    Biedt methoden voor:
    - Uitgebreide diagnostische rapporten
    - Identificatie van interventie-prioriteiten
    - Monitoring van ontwikkeling over tijd
    """
    
    def __init__(
        self, 
        relationship_graph: RelationshipGraph,
        affective_metrics: Optional[AffectiveMetrics] = None
    ):
        """
        Initialiseer diagnostic tools.
        
        Args:
            relationship_graph: RelationshipGraph met organisatiedata
            affective_metrics: Optioneel AffectiveMetrics object
        """
        self.graph = relationship_graph
        self.metrics = affective_metrics or AffectiveMetrics(relationship_graph)
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """
        Genereer een uitgebreid diagnostisch rapport.
        
        Returns:
            Dict met volledige diagnose inclusief:
            - Algemene statistieken
            - Affectieve metrieken per dimensie
            - Risicogroepen
            - Aanbevelingen
        """
        report = {
            'vereniging_metadata': self.graph.get_metadata(),
            'netwerk_statistieken': self.graph.get_graph_metrics(),
            'affectieve_dimensies': {},
            'risico_analyse': {},
            'prioritaire_interventies': [],
            'overall_health': {},
        }
        
        # Verzamel affectieve metrieken
        report['affectieve_dimensies'] = {
            'emotioneel_klimaat': self.metrics.calculate_emotional_climate(),
            'relationele_kwaliteit': self.metrics.calculate_relational_quality(),
            'psychologische_veiligheid': self.metrics.calculate_psychological_safety(),
            'culturele_cohesie': self.metrics.calculate_cultural_cohesion(),
        }
        
        # Risico analyse
        report['risico_analyse'] = {
            'uitval_risico': self.metrics.calculate_dropout_risk_indicators(),
            'geisoleerde_leden': self.graph.identify_isolated_members(),
            'communities': self.graph.detect_communities(),
        }
        
        # Overall health scores
        report['overall_health'] = self.metrics.calculate_comprehensive_score()
        
        # Genereer interventie prioriteiten
        report['prioritaire_interventies'] = \
            self._generate_intervention_priorities(report)
        
        return report
    
    def _generate_intervention_priorities(
        self, 
        report: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Genereer geprioritiseerde lijst van interventies.
        
        Args:
            report: Het diagnostisch rapport
            
        Returns:
            List van interventie aanbevelingen met prioriteit
        """
        priorities = []
        
        # Check emotioneel klimaat
        emotional = report['affectieve_dimensies']['emotioneel_klimaat']
        if emotional['percentage_laag_welzijn'] > 20:
            priorities.append({
                'prioriteit': 'HOOG',
                'dimensie': 'Emotioneel Klimaat',
                'probleem': f"{emotional['percentage_laag_welzijn']:.1f}% van leden heeft laag emotioneel welzijn",
                'aanbeveling': 'Organiseer welzijnscheck gesprekken en implementeer peer support programma',
                'betrokken_leden': report['risico_analyse']['uitval_risico']['leden_met_laag_welzijn'],
            })
        
        # Check geïsoleerde leden
        isolated_count = len(report['risico_analyse']['geisoleerde_leden'])
        total_members = report['netwerk_statistieken']['aantal_leden']
        if total_members > 0 and (isolated_count / total_members) > 0.15:
            priorities.append({
                'prioriteit': 'HOOG',
                'dimensie': 'Relationele Kwaliteit',
                'probleem': f"{isolated_count} leden ({100*isolated_count/total_members:.1f}%) zijn sociaal geïsoleerd",
                'aanbeveling': 'Start buddy-systeem en faciliteer informele sociale momenten',
                'betrokken_leden': report['risico_analyse']['geisoleerde_leden'],
            })
        
        # Check psychologische veiligheid
        safety = report['affectieve_dimensies']['psychologische_veiligheid']
        if safety['percentage_lage_veiligheid'] > 25:
            priorities.append({
                'prioriteit': 'HOOG',
                'dimensie': 'Psychologische Veiligheid',
                'probleem': f"{safety['percentage_lage_veiligheid']:.1f}% van relaties heeft lage psychologische veiligheid",
                'aanbeveling': 'Implementeer veiligheidstraining voor coaches en leiders, stel gedragscode op',
                'betrokken_leden': [],
            })
        
        # Check culturele cohesie
        cultural = report['affectieve_dimensies']['culturele_cohesie']
        if cultural['fragmentatie'] > 0.4:
            priorities.append({
                'prioriteit': 'GEMIDDELD',
                'dimensie': 'Culturele Cohesie',
                'probleem': f"Hoge fragmentatie ({100*cultural['fragmentatie']:.1f}%) wijst op verdeeld netwerk",
                'aanbeveling': 'Organiseer verenigings-brede activiteiten om subgroepen te verbinden',
                'betrokken_leden': [],
            })
        
        # Check relationele sterkte
        relational = report['affectieve_dimensies']['relationele_kwaliteit']
        if relational.get('percentage_sterke_relaties', 0) < 30:
            priorities.append({
                'prioriteit': 'GEMIDDELD',
                'dimensie': 'Relationele Kwaliteit',
                'probleem': f"Slechts {relational.get('percentage_sterke_relaties', 0):.1f}% van relaties is sterk",
                'aanbeveling': 'Faciliteer diepere connecties door teambuilding en mentor programmas',
                'betrokken_leden': report['risico_analyse']['uitval_risico']['leden_met_zwakke_relaties'],
            })
        
        # Sorteer op prioriteit
        priority_order = {'HOOG': 0, 'GEMIDDELD': 1, 'LAAG': 2}
        priorities.sort(key=lambda x: priority_order.get(x['prioriteit'], 3))
        
        return priorities
    
    def identify_key_connectors(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Identificeer belangrijke sociale knooppunten in het netwerk.
        
        Args:
            top_n: Aantal top connectors te identificeren
            
        Returns:
            List van key connectors met hun scores
        """
        centrality = self.graph.calculate_centrality_measures()
        
        if not centrality or 'degree' not in centrality:
            return []
        
        # Combineer verschillende centraliteits scores
        combined_scores = {}
        for node in self.graph.graph.nodes():
            score = (
                centrality['degree'].get(node, 0) * 0.3 +
                centrality['betweenness'].get(node, 0) * 0.3 +
                centrality['closeness'].get(node, 0) * 0.2 +
                centrality['eigenvector'].get(node, 0) * 0.2
            )
            combined_scores[node] = score
        
        # Sorteer en neem top N
        sorted_nodes = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        key_connectors = []
        for node_id, score in sorted_nodes:
            attrs = self.graph.get_member_attributes(node_id)
            key_connectors.append({
                'lid_id': node_id,
                'naam': attrs.get('naam', node_id),
                'rol': attrs.get('rol', 'onbekend'),
                'connector_score': score,
                'aantal_connecties': self.graph.graph.degree(node_id),
            })
        
        return key_connectors
    
    def analyze_community_health(self) -> List[Dict[str, Any]]:
        """
        Analyseer de gezondheid van elke community/subgroep.
        
        Returns:
            List van community analyses
        """
        communities = self.graph.detect_communities()
        
        community_analyses = []
        for idx, community in enumerate(communities):
            # Bereken gemiddelde welzijn in deze community
            welzijn_scores = []
            for member_id in community:
                attrs = self.graph.get_member_attributes(member_id)
                if 'emotionele_welzijn' in attrs:
                    welzijn_scores.append(attrs['emotionele_welzijn'])
            
            # Bereken interne vs externe connecties
            internal_edges = 0
            external_edges = 0
            for member_id in community:
                neighbors = self.graph.get_neighbors(member_id)
                for neighbor in neighbors:
                    if neighbor in community:
                        internal_edges += 1
                    else:
                        external_edges += 1
            
            # Compenseer voor dubbel tellen
            internal_edges = internal_edges // 2
            
            community_analyses.append({
                'community_id': idx,
                'grootte': len(community),
                'leden': community,
                'gemiddeld_welzijn': float(np.mean(welzijn_scores)) if welzijn_scores else 0.0,
                'interne_connecties': internal_edges,
                'externe_connecties': external_edges,
                'cohesie_ratio': internal_edges / (internal_edges + external_edges) if (internal_edges + external_edges) > 0 else 0.0,
            })
        
        return community_analyses
    
    def generate_individual_report(self, member_id: str) -> Dict[str, Any]:
        """
        Genereer een individueel rapport voor een specifiek lid.
        
        Args:
            member_id: ID van het lid
            
        Returns:
            Dict met individuele analyse
        """
        if member_id not in self.graph.graph:
            raise ValueError(f"Lid {member_id} niet gevonden")
        
        attrs = self.graph.get_member_attributes(member_id)
        neighbors = self.graph.get_neighbors(member_id)
        
        # Bereken centraliteit voor dit lid
        centrality = self.graph.calculate_centrality_measures()
        
        # Analyseer relaties
        relatie_analyse = {
            'sterke_relaties': 0,
            'gemiddelde_relaties': 0,
            'zwakke_relaties': 0,
        }
        
        for neighbor in neighbors:
            rel_attrs = self.graph.get_relationship_attributes(member_id, neighbor)
            if 'sterkte' in rel_attrs:
                if rel_attrs['sterkte'] >= 7:
                    relatie_analyse['sterke_relaties'] += 1
                elif rel_attrs['sterkte'] >= 4:
                    relatie_analyse['gemiddelde_relaties'] += 1
                else:
                    relatie_analyse['zwakke_relaties'] += 1
        
        # Identificeer community
        communities = self.graph.detect_communities()
        member_community = None
        for idx, community in enumerate(communities):
            if member_id in community:
                member_community = idx
                break
        
        report = {
            'lid_id': member_id,
            'basis_info': attrs,
            'netwerk_positie': {
                'aantal_connecties': len(neighbors),
                'degree_centrality': centrality['degree'].get(member_id, 0),
                'betweenness_centrality': centrality['betweenness'].get(member_id, 0),
                'closeness_centrality': centrality['closeness'].get(member_id, 0),
                'eigenvector_centrality': centrality['eigenvector'].get(member_id, 0),
            },
            'relatie_kwaliteit': relatie_analyse,
            'community': member_community,
            'risico_factoren': [],
        }
        
        # Identificeer risico factoren
        if attrs.get('emotionele_welzijn', 10) < 4:
            report['risico_factoren'].append('Laag emotioneel welzijn')
        
        if len(neighbors) < 2:
            report['risico_factoren'].append('Sociaal geïsoleerd')
        
        if relatie_analyse['sterke_relaties'] == 0 and len(neighbors) > 0:
            report['risico_factoren'].append('Geen sterke relaties')
        
        return report


# Import numpy voor community analysis
import numpy as np
from typing import Optional
