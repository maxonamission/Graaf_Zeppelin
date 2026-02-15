"""
RelationshipGraph: Graph-based model voor sociale relaties in sportverenigingen

Dit module implementeert een graaf-theoretische benadering voor het modelleren
van sociale en affectieve relaties binnen sportverenigingen.
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Optional, Tuple, Any


class RelationshipGraph:
    """
    Een graaf die de relaties tussen leden van een sportvereniging modelleert.
    
    Nodes vertegenwoordigen individuen (leden, coaches, vrijwilligers)
    Edges vertegenwoordigen relaties met affectieve kenmerken zoals:
    - Emotionele verbondenheid
    - Vertrouwen
    - Frequentie van interactie
    - Kwaliteit van communicatie
    """
    
    def __init__(self):
        """Initialiseer een lege relatiegraph."""
        self.graph = nx.Graph()
        self._metadata = {
            'naam_vereniging': None,
            'datum_analyse': None,
            'beschrijving': None
        }
    
    def add_member(
        self, 
        member_id: str, 
        **attributes: Any
    ) -> None:
        """
        Voeg een lid toe aan de vereniging.
        
        Args:
            member_id: Unieke identificatie van het lid
            **attributes: Extra attributen zoals:
                - naam: Naam van het lid
                - rol: (speler, coach, vrijwilliger, etc.)
                - leeftijd: Leeftijdsgroep
                - anciënniteit: Jaren lid
                - emotionele_welzijn: Score 0-10
        """
        self.graph.add_node(member_id, **attributes)
    
    def add_relationship(
        self,
        member1_id: str,
        member2_id: str,
        **attributes: Any
    ) -> None:
        """
        Voeg een relatie toe tussen twee leden.
        
        Args:
            member1_id: ID van eerste lid
            member2_id: ID van tweede lid
            **attributes: Relatie attributen zoals:
                - sterkte: Sterkte van relatie (0-10)
                - vertrouwen: Vertrouwensniveau (0-10)
                - frequentie: Contactfrequentie (0-10)
                - emotionele_steun: Mate van emotionele steun (0-10)
                - psychologische_veiligheid: Score (0-10)
        """
        self.graph.add_edge(member1_id, member2_id, **attributes)
    
    def get_member_attributes(self, member_id: str) -> Dict:
        """Haal attributen van een lid op."""
        if member_id not in self.graph:
            raise ValueError(f"Lid {member_id} niet gevonden in graaf")
        return dict(self.graph.nodes[member_id])
    
    def get_relationship_attributes(
        self, 
        member1_id: str, 
        member2_id: str
    ) -> Dict:
        """Haal attributen van een relatie op."""
        if not self.graph.has_edge(member1_id, member2_id):
            raise ValueError(f"Geen relatie tussen {member1_id} en {member2_id}")
        return dict(self.graph[member1_id][member2_id])
    
    def get_neighbors(self, member_id: str) -> List[str]:
        """Haal alle directe connecties van een lid op."""
        if member_id not in self.graph:
            raise ValueError(f"Lid {member_id} niet gevonden in graaf")
        return list(self.graph.neighbors(member_id))
    
    def calculate_centrality_measures(self) -> Dict[str, Dict[str, float]]:
        """
        Bereken verschillende centraliteitsmetrieken voor alle leden.
        
        Centraliteit geeft aan hoe belangrijk/centraal een lid is in het netwerk.
        Hoge centraliteit kan wijzen op belangrijke sociale knooppunten.
        
        Returns:
            Dict met voor elk lid hun centraliteitsscores
        """
        if len(self.graph) == 0:
            return {}
        
        centrality = {}
        
        # Degree centrality: aantal directe connecties
        centrality['degree'] = nx.degree_centrality(self.graph)
        
        # Betweenness centrality: hoe vaak ligt iemand op kortste pad tussen anderen
        centrality['betweenness'] = nx.betweenness_centrality(self.graph)
        
        # Closeness centrality: gemiddelde afstand tot alle anderen
        if nx.is_connected(self.graph):
            centrality['closeness'] = nx.closeness_centrality(self.graph)
        else:
            centrality['closeness'] = {}
            for component in nx.connected_components(self.graph):
                subgraph = self.graph.subgraph(component)
                closeness = nx.closeness_centrality(subgraph)
                centrality['closeness'].update(closeness)
        
        # Eigenvector centrality: connecties met belangrijke mensen
        try:
            centrality['eigenvector'] = nx.eigenvector_centrality(
                self.graph, 
                max_iter=1000
            )
        except nx.PowerIterationFailedConvergence:
            centrality['eigenvector'] = {
                node: 0.0 for node in self.graph.nodes()
            }
        
        return centrality
    
    def identify_isolated_members(
        self, 
        threshold: int = 2
    ) -> List[str]:
        """
        Identificeer geïsoleerde leden (weinig connecties).
        
        Args:
            threshold: Minimaal aantal connecties (standaard 2)
            
        Returns:
            List van lid IDs met te weinig connecties
        """
        isolated = []
        for node in self.graph.nodes():
            if self.graph.degree(node) < threshold:
                isolated.append(node)
        return isolated
    
    def detect_communities(self) -> List[List[str]]:
        """
        Detecteer gemeenschappen/groepen binnen de vereniging.
        
        Returns:
            List van gemeenschappen (elk een list van lid IDs)
        """
        if len(self.graph) == 0:
            return []
        
        # Greedy modularity communities
        communities = nx.community.greedy_modularity_communities(self.graph)
        return [list(community) for community in communities]
    
    def calculate_clustering_coefficient(self) -> Dict[str, float]:
        """
        Bereken clustering coëfficiënt per lid.
        
        Hoog = vrienden van dit lid zijn ook vrienden met elkaar
        Laag = dit lid verbindt verschillende groepen
        
        Returns:
            Dict met clustering coëfficiënt per lid
        """
        return nx.clustering(self.graph)
    
    def get_graph_metrics(self) -> Dict[str, Any]:
        """
        Haal algemene graaf metrieken op.
        
        Returns:
            Dict met diverse netwerk-brede metrieken
        """
        metrics = {
            'aantal_leden': self.graph.number_of_nodes(),
            'aantal_relaties': self.graph.number_of_edges(),
        }
        
        if len(self.graph) > 0:
            metrics['gemiddelde_graad'] = sum(
                dict(self.graph.degree()).values()
            ) / len(self.graph)
            
            metrics['is_verbonden'] = nx.is_connected(self.graph)
            
            if nx.is_connected(self.graph):
                metrics['diameter'] = nx.diameter(self.graph)
                metrics['gemiddelde_pad_lengte'] = \
                    nx.average_shortest_path_length(self.graph)
            
            metrics['dichtheid'] = nx.density(self.graph)
            
            metrics['aantal_componenten'] = \
                nx.number_connected_components(self.graph)
            
            metrics['gemiddelde_clustering'] = \
                nx.average_clustering(self.graph)
        
        return metrics
    
    def set_metadata(self, **metadata: Any) -> None:
        """Stel metadata van de vereniging in."""
        self._metadata.update(metadata)
    
    def get_metadata(self) -> Dict[str, Any]:
        """Haal metadata van de vereniging op."""
        return self._metadata.copy()
    
    def export_to_dict(self) -> Dict[str, Any]:
        """
        Exporteer de volledige graaf naar een dictionary.
        
        Returns:
            Dict met alle node/edge data en metadata
        """
        return {
            'metadata': self._metadata,
            'nodes': [
                {'id': node, **self.graph.nodes[node]}
                for node in self.graph.nodes()
            ],
            'edges': [
                {
                    'source': u,
                    'target': v,
                    **self.graph[u][v]
                }
                for u, v in self.graph.edges()
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RelationshipGraph':
        """
        Importeer een graaf vanuit een dictionary.
        
        Args:
            data: Dict met nodes, edges en metadata
            
        Returns:
            RelationshipGraph instantie
        """
        graph = cls()
        
        if 'metadata' in data:
            graph.set_metadata(**data['metadata'])
        
        for node_data in data.get('nodes', []):
            node_id = node_data.pop('id')
            graph.add_member(node_id, **node_data)
        
        for edge_data in data.get('edges', []):
            source = edge_data.pop('source')
            target = edge_data.pop('target')
            graph.add_relationship(source, target, **edge_data)
        
        return graph
