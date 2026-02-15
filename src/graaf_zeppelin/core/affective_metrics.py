"""
AffectiveMetrics: Metrieken voor affectieve dynamiek in sportverenigingen

Dit module berekent metrieken voor emotionele, relationele en culturele aspecten
van de vereniging om de affectieve dynamiek te kwantificeren.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from .relationship_graph import RelationshipGraph


class AffectiveMetrics:
    """
    Berekent affectieve metrieken op basis van de relatie graaf.
    
    Focus op drie dimensies:
    1. Emotionele klimaat: welzijn, betrokkenheid, enthousiasme
    2. Relationele kwaliteit: vertrouwen, steun, verbondenheid
    3. Culturele cohesie: gedeelde waarden, inclusie, saamhorigheid
    """
    
    def __init__(self, relationship_graph: RelationshipGraph):
        """
        Initialiseer affective metrics calculator.
        
        Args:
            relationship_graph: RelationshipGraph met lid- en relatiedata
        """
        self.graph = relationship_graph
    
    def calculate_emotional_climate(self) -> Dict[str, float]:
        """
        Bereken metrieken voor het emotionele klimaat.
        
        Returns:
            Dict met emotionele klimaat indicatoren:
            - gemiddeld_welzijn: Gemiddelde emotionele welzijn score
            - spreiding_welzijn: Standaarddeviatie van welzijn
            - percentage_hoog_welzijn: % leden met hoog welzijn (>7)
            - percentage_laag_welzijn: % leden met laag welzijn (<4)
        """
        welzijn_scores = []
        
        for node in self.graph.graph.nodes():
            attrs = self.graph.get_member_attributes(node)
            if 'emotionele_welzijn' in attrs:
                welzijn_scores.append(attrs['emotionele_welzijn'])
        
        if not welzijn_scores:
            return {
                'gemiddeld_welzijn': 0.0,
                'spreiding_welzijn': 0.0,
                'percentage_hoog_welzijn': 0.0,
                'percentage_laag_welzijn': 0.0,
            }
        
        welzijn_array = np.array(welzijn_scores)
        
        return {
            'gemiddeld_welzijn': float(np.mean(welzijn_array)),
            'spreiding_welzijn': float(np.std(welzijn_array)),
            'percentage_hoog_welzijn': float(
                100 * np.sum(welzijn_array > 7) / len(welzijn_array)
            ),
            'percentage_laag_welzijn': float(
                100 * np.sum(welzijn_array < 4) / len(welzijn_array)
            ),
        }
    
    def calculate_relational_quality(self) -> Dict[str, float]:
        """
        Bereken metrieken voor relationele kwaliteit.
        
        Returns:
            Dict met relationele kwaliteit indicatoren:
            - gemiddelde_relatie_sterkte: Gemiddelde sterkte van relaties
            - gemiddeld_vertrouwen: Gemiddeld vertrouwensniveau
            - gemiddelde_emotionele_steun: Gemiddelde mate van emotionele steun
            - percentage_sterke_relaties: % relaties met hoge sterkte (>7)
        """
        relatie_sterkte = []
        vertrouwen_scores = []
        emotionele_steun_scores = []
        
        for u, v in self.graph.graph.edges():
            attrs = self.graph.get_relationship_attributes(u, v)
            
            if 'sterkte' in attrs:
                relatie_sterkte.append(attrs['sterkte'])
            if 'vertrouwen' in attrs:
                vertrouwen_scores.append(attrs['vertrouwen'])
            if 'emotionele_steun' in attrs:
                emotionele_steun_scores.append(attrs['emotionele_steun'])
        
        metrics = {}
        
        if relatie_sterkte:
            sterkte_array = np.array(relatie_sterkte)
            metrics['gemiddelde_relatie_sterkte'] = float(np.mean(sterkte_array))
            metrics['percentage_sterke_relaties'] = float(
                100 * np.sum(sterkte_array > 7) / len(sterkte_array)
            )
        else:
            metrics['gemiddelde_relatie_sterkte'] = 0.0
            metrics['percentage_sterke_relaties'] = 0.0
        
        if vertrouwen_scores:
            metrics['gemiddeld_vertrouwen'] = float(np.mean(vertrouwen_scores))
        else:
            metrics['gemiddeld_vertrouwen'] = 0.0
        
        if emotionele_steun_scores:
            metrics['gemiddelde_emotionele_steun'] = float(
                np.mean(emotionele_steun_scores)
            )
        else:
            metrics['gemiddelde_emotionele_steun'] = 0.0
        
        return metrics
    
    def calculate_psychological_safety(self) -> Dict[str, float]:
        """
        Bereken psychologische veiligheid metrieken.
        
        Psychologische veiligheid is cruciaal voor duurzame deelname.
        
        Returns:
            Dict met psychologische veiligheid indicatoren:
            - gemiddelde_psychologische_veiligheid: Gemiddelde score
            - percentage_hoge_veiligheid: % relaties met hoge veiligheid (>7)
            - percentage_lage_veiligheid: % relaties met lage veiligheid (<4)
        """
        veiligheid_scores = []
        
        for u, v in self.graph.graph.edges():
            attrs = self.graph.get_relationship_attributes(u, v)
            if 'psychologische_veiligheid' in attrs:
                veiligheid_scores.append(attrs['psychologische_veiligheid'])
        
        if not veiligheid_scores:
            return {
                'gemiddelde_psychologische_veiligheid': 0.0,
                'percentage_hoge_veiligheid': 0.0,
                'percentage_lage_veiligheid': 0.0,
            }
        
        veiligheid_array = np.array(veiligheid_scores)
        
        return {
            'gemiddelde_psychologische_veiligheid': float(
                np.mean(veiligheid_array)
            ),
            'percentage_hoge_veiligheid': float(
                100 * np.sum(veiligheid_array > 7) / len(veiligheid_array)
            ),
            'percentage_lage_veiligheid': float(
                100 * np.sum(veiligheid_array < 4) / len(veiligheid_array)
            ),
        }
    
    def calculate_cultural_cohesion(self) -> Dict[str, float]:
        """
        Bereken culturele cohesie metrieken.
        
        Returns:
            Dict met culturele cohesie indicatoren:
            - netwerk_dichtheid: Hoe dicht verbonden is het netwerk
            - gemiddelde_clustering: Mate van lokale samenhang
            - modulariteit: Sterkte van subgroepen
            - fragmentatie: Mate van verdeeldheid (1 - grootste component %)
        """
        graph_metrics = self.graph.get_graph_metrics()
        
        metrics = {
            'netwerk_dichtheid': graph_metrics.get('dichtheid', 0.0),
            'gemiddelde_clustering': graph_metrics.get(
                'gemiddelde_clustering', 0.0
            ),
        }
        
        # Bereken modulariteit van gedetecteerde communities
        if len(self.graph.graph) > 0:
            communities = self.graph.detect_communities()
            if communities:
                # Converteer naar partition format voor modularity berekening
                partition = {}
                for idx, community in enumerate(communities):
                    for node in community:
                        partition[node] = idx
                
                try:
                    import networkx.algorithms.community as nx_comm
                    metrics['modulariteit'] = float(
                        nx_comm.modularity(
                            self.graph.graph,
                            communities
                        )
                    )
                except:
                    metrics['modulariteit'] = 0.0
            else:
                metrics['modulariteit'] = 0.0
            
            # Bereken fragmentatie
            if graph_metrics['aantal_leden'] > 0:
                largest_component = max(
                    (len(c) for c in self.graph.graph.subgraphs()),
                    default=0
                ) if len(self.graph.graph) > 0 else 0
                
                metrics['fragmentatie'] = float(
                    1.0 - (largest_component / graph_metrics['aantal_leden'])
                )
            else:
                metrics['fragmentatie'] = 0.0
        else:
            metrics['modulariteit'] = 0.0
            metrics['fragmentatie'] = 0.0
        
        return metrics
    
    def calculate_dropout_risk_indicators(self) -> Dict[str, any]:
        """
        Identificeer indicatoren voor uitvalrisico.
        
        Returns:
            Dict met uitval risico indicatoren:
            - leden_met_laag_welzijn: List van lid IDs
            - geisoleerde_leden: List van lid IDs
            - leden_met_zwakke_relaties: List van lid IDs
            - totaal_risico_leden: Aantal unieke leden met risico
        """
        at_risk = {
            'leden_met_laag_welzijn': [],
            'geisoleerde_leden': [],
            'leden_met_zwakke_relaties': [],
        }
        
        # Identificeer leden met laag emotioneel welzijn
        for node in self.graph.graph.nodes():
            attrs = self.graph.get_member_attributes(node)
            if 'emotionele_welzijn' in attrs:
                if attrs['emotionele_welzijn'] < 4:
                    at_risk['leden_met_laag_welzijn'].append(node)
        
        # Identificeer geïsoleerde leden
        at_risk['geisoleerde_leden'] = self.graph.identify_isolated_members(
            threshold=2
        )
        
        # Identificeer leden met alleen zwakke relaties
        for node in self.graph.graph.nodes():
            neighbors = self.graph.get_neighbors(node)
            if neighbors:
                sterke_relaties = 0
                for neighbor in neighbors:
                    attrs = self.graph.get_relationship_attributes(node, neighbor)
                    if 'sterkte' in attrs and attrs['sterkte'] >= 5:
                        sterke_relaties += 1
                
                if sterke_relaties == 0:
                    at_risk['leden_met_zwakke_relaties'].append(node)
        
        # Bereken totaal aantal unieke leden met risico
        alle_risico_leden = set(
            at_risk['leden_met_laag_welzijn'] +
            at_risk['geisoleerde_leden'] +
            at_risk['leden_met_zwakke_relaties']
        )
        at_risk['totaal_risico_leden'] = len(alle_risico_leden)
        
        return at_risk
    
    def calculate_comprehensive_score(self) -> Dict[str, float]:
        """
        Bereken een uitgebreide affectieve dynamiek score.
        
        Combineert alle dimensies tot overall health scores.
        
        Returns:
            Dict met comprehensive scores (0-10 schaal):
            - emotioneel_klimaat_score: Overall emotionele gezondheid
            - relationele_kwaliteit_score: Overall relationele gezondheid
            - psychologische_veiligheid_score: Overall veiligheidsniveau
            - culturele_cohesie_score: Overall culturele samenhang
            - totale_affectieve_gezondheid: Gewogen gemiddelde van alle scores
        """
        scores = {}
        
        # Emotioneel klimaat score
        emotional = self.calculate_emotional_climate()
        scores['emotioneel_klimaat_score'] = float(
            emotional['gemiddeld_welzijn']
        )
        
        # Relationele kwaliteit score
        relational = self.calculate_relational_quality()
        relational_components = [
            relational.get('gemiddelde_relatie_sterkte', 0),
            relational.get('gemiddeld_vertrouwen', 0),
            relational.get('gemiddelde_emotionele_steun', 0),
        ]
        scores['relationele_kwaliteit_score'] = float(
            np.mean([x for x in relational_components if x > 0]) 
            if any(x > 0 for x in relational_components) else 0.0
        )
        
        # Psychologische veiligheid score
        safety = self.calculate_psychological_safety()
        scores['psychologische_veiligheid_score'] = float(
            safety['gemiddelde_psychologische_veiligheid']
        )
        
        # Culturele cohesie score (genormaliseerd naar 0-10)
        cultural = self.calculate_cultural_cohesion()
        # Dichtheid en clustering zijn 0-1, modularity kan negatief tot 1 zijn
        cohesion_components = [
            cultural.get('netwerk_dichtheid', 0) * 10,
            cultural.get('gemiddelde_clustering', 0) * 10,
            max(0, cultural.get('modulariteit', 0)) * 10,  # Alleen positieve modularity
            (1 - cultural.get('fragmentatie', 1)) * 10,  # Inverse fragmentatie
        ]
        scores['culturele_cohesie_score'] = float(
            np.mean(cohesion_components)
        )
        
        # Totale affectieve gezondheid (gewogen gemiddelde)
        # Alle dimensies evenveel gewicht
        all_scores = [
            scores['emotioneel_klimaat_score'],
            scores['relationele_kwaliteit_score'],
            scores['psychologische_veiligheid_score'],
            scores['culturele_cohesie_score'],
        ]
        scores['totale_affectieve_gezondheid'] = float(
            np.mean([s for s in all_scores if s > 0])
            if any(s > 0 for s in all_scores) else 0.0
        )
        
        return scores
