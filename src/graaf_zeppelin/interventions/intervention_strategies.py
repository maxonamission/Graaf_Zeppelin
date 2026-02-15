"""
InterventionStrategies: Interventiestrategieën voor versterking affectieve dynamiek

Dit module biedt concrete interventiestrategieën om de affectieve dynamiek
te versterken en duurzame sportdeelname te bevorderen.
"""

from typing import Dict, List, Any, Optional
from ..core.relationship_graph import RelationshipGraph


class InterventionStrategies:
    """
    Biedt evidence-based interventiestrategieën voor verschillende scenario's.
    
    Focus op:
    - Versterken van psychologische veiligheid
    - Verminderen van uitval
    - Verbeteren van relationele kwaliteit
    - Verhogen van emotioneel welzijn
    """
    
    def __init__(self, relationship_graph: RelationshipGraph):
        """
        Initialiseer intervention strategies.
        
        Args:
            relationship_graph: RelationshipGraph met organisatiedata
        """
        self.graph = relationship_graph
    
    def suggest_buddy_pairs(
        self, 
        isolated_members: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Stel buddy-paren voor om geïsoleerde leden te integreren.
        
        Args:
            isolated_members: List van geïsoleerde lid IDs
            
        Returns:
            List van voorgestelde buddy-paren met rationale
        """
        if isolated_members is None:
            isolated_members = self.graph.identify_isolated_members()
        
        if not isolated_members:
            return []
        
        # Bereken centraliteit om goede buddies te vinden
        centrality = self.graph.calculate_centrality_measures()
        
        buddy_pairs = []
        
        for isolated_id in isolated_members:
            isolated_attrs = self.graph.get_member_attributes(isolated_id)
            
            # Zoek potentiële buddies: hoge centrality, vergelijkbare rol/leeftijd
            candidates = []
            for node in self.graph.graph.nodes():
                if node == isolated_id:
                    continue
                
                node_attrs = self.graph.get_member_attributes(node)
                
                # Bereken match score
                match_score = centrality['degree'].get(node, 0)
                
                # Bonus voor vergelijkbare leeftijd
                if 'leeftijd' in isolated_attrs and 'leeftijd' in node_attrs:
                    if abs(isolated_attrs['leeftijd'] - node_attrs['leeftijd']) <= 5:
                        match_score += 0.2
                
                # Bonus voor vergelijkbare rol
                if isolated_attrs.get('rol') == node_attrs.get('rol'):
                    match_score += 0.15
                
                candidates.append((node, match_score))
            
            # Selecteer beste kandidaat
            if candidates:
                candidates.sort(key=lambda x: x[1], reverse=True)
                best_buddy_id, score = candidates[0]
                best_buddy_attrs = self.graph.get_member_attributes(best_buddy_id)
                
                buddy_pairs.append({
                    'geisoleerd_lid': {
                        'id': isolated_id,
                        'naam': isolated_attrs.get('naam', isolated_id),
                        'rol': isolated_attrs.get('rol', 'onbekend'),
                    },
                    'voorgestelde_buddy': {
                        'id': best_buddy_id,
                        'naam': best_buddy_attrs.get('naam', best_buddy_id),
                        'rol': best_buddy_attrs.get('rol', 'onbekend'),
                    },
                    'rationale': self._generate_buddy_rationale(
                        isolated_attrs, 
                        best_buddy_attrs
                    ),
                    'match_score': score,
                })
        
        return buddy_pairs
    
    def _generate_buddy_rationale(
        self, 
        isolated_attrs: Dict, 
        buddy_attrs: Dict
    ) -> str:
        """Genereer uitleg waarom dit een goed buddy-paar is."""
        reasons = []
        
        if isolated_attrs.get('rol') == buddy_attrs.get('rol'):
            reasons.append(f"beide hebben rol '{isolated_attrs.get('rol')}'")
        
        if 'leeftijd' in isolated_attrs and 'leeftijd' in buddy_attrs:
            if abs(isolated_attrs['leeftijd'] - buddy_attrs['leeftijd']) <= 5:
                reasons.append("vergelijkbare leeftijd")
        
        reasons.append("buddy heeft sterke sociale positie in vereniging")
        
        return "Goed match omdat " + " en ".join(reasons)
    
    def suggest_team_building_activities(
        self,
        weak_communities: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Stel teambuilding activiteiten voor.
        
        Args:
            weak_communities: IDs van communities die versterking nodig hebben
            
        Returns:
            List van voorgestelde activiteiten
        """
        activities = []
        
        # Algemene verenigings-brede activiteiten
        graph_metrics = self.graph.get_graph_metrics()
        if graph_metrics.get('aantal_componenten', 1) > 1:
            activities.append({
                'type': 'Verenigings-breed',
                'activiteit': 'Sociale bijeenkomst',
                'doel': 'Verbinden van gescheiden subgroepen',
                'omschrijving': 'Organiseer informele bijeenkomst (BBQ, spelletjesavond) waar alle leden samen komen',
                'prioriteit': 'HOOG',
                'verwachte_impact': 'Verhoogt netwerk dichtheid en verkleint fragmentatie',
            })
        
        # Activiteiten voor zwakke cohesie
        if graph_metrics.get('gemiddelde_clustering', 0) < 0.3:
            activities.append({
                'type': 'Kleine groepen',
                'activiteit': 'Mentorcirkels',
                'doel': 'Versterken van lokale clusters',
                'omschrijving': 'Vorm kleine groepen (5-7 leden) met vaste mentor voor regelmatige check-ins',
                'prioriteit': 'GEMIDDELD',
                'verwachte_impact': 'Verhoogt clustering coëfficiënt en emotionele steun',
            })
        
        # Activiteiten voor relationele kwaliteit
        activities.append({
            'type': 'Team ontwikkeling',
            'activiteit': 'Reflectie sessies',
            'doel': 'Verdiepen van relaties',
            'omschrijving': 'Faciliteer gestructureerde sessies waar leden ervaringen en emoties delen',
            'prioriteit': 'GEMIDDELD',
            'verwachte_impact': 'Verhoogt vertrouwen en psychologische veiligheid',
        })
        
        # Activiteiten voor psychologische veiligheid
        activities.append({
            'type': 'Training',
            'activiteit': 'Psychologische veiligheid workshop',
            'doel': 'Bewustwording en skills',
            'omschrijving': 'Train coaches en leiders in creëren van psychologisch veilige omgeving',
            'prioriteit': 'HOOG',
            'verwachte_impact': 'Verbetert psychologische veiligheid scores in alle relaties',
        })
        
        return activities
    
    def create_action_plan(
        self,
        priorities: List[Dict[str, Any]],
        timeline_weeks: int = 12
    ) -> Dict[str, Any]:
        """
        Creëer een uitvoerbaar actieplan.
        
        Args:
            priorities: Lijst van prioritaire interventies
            timeline_weeks: Tijdsspanne voor het plan (weken)
            
        Returns:
            Dict met gestructureerd actieplan
        """
        action_plan = {
            'tijdsspanne_weken': timeline_weeks,
            'fasen': [],
            'meetmomenten': [],
            'success_criteria': [],
        }
        
        # Fase 1: Eerste 4 weken - Urgente zaken
        fase1_acties = []
        for priority in priorities:
            if priority.get('prioriteit') == 'HOOG':
                fase1_acties.append({
                    'actie': priority['aanbeveling'],
                    'dimensie': priority['dimensie'],
                    'betrokkenen': priority.get('betrokken_leden', []),
                })
        
        if fase1_acties:
            action_plan['fasen'].append({
                'fase': 1,
                'periode': 'Week 1-4',
                'focus': 'Urgente interventies',
                'acties': fase1_acties,
            })
        
        # Fase 2: Week 5-8 - Structurele verbeteringen
        fase2_acties = []
        for priority in priorities:
            if priority.get('prioriteit') == 'GEMIDDELD':
                fase2_acties.append({
                    'actie': priority['aanbeveling'],
                    'dimensie': priority['dimensie'],
                    'betrokkenen': priority.get('betrokken_leden', []),
                })
        
        # Voeg buddy-systeem toe indien nodig
        isolated = self.graph.identify_isolated_members()
        if isolated:
            fase2_acties.append({
                'actie': 'Implementeer buddy-systeem voor geïsoleerde leden',
                'dimensie': 'Relationele Kwaliteit',
                'betrokkenen': isolated,
            })
        
        if fase2_acties:
            action_plan['fasen'].append({
                'fase': 2,
                'periode': 'Week 5-8',
                'focus': 'Structurele verbeteringen',
                'acties': fase2_acties,
            })
        
        # Fase 3: Week 9-12 - Consolidatie en monitoring
        action_plan['fasen'].append({
            'fase': 3,
            'periode': 'Week 9-12',
            'focus': 'Consolidatie en evaluatie',
            'acties': [
                {
                    'actie': 'Evalueer effectiviteit van interventies',
                    'dimensie': 'Monitoring',
                    'betrokkenen': [],
                },
                {
                    'actie': 'Herhaal diagnostische meting',
                    'dimensie': 'Monitoring',
                    'betrokkenen': [],
                },
                {
                    'actie': 'Pas actieplan aan op basis van resultaten',
                    'dimensie': 'Monitoring',
                    'betrokkenen': [],
                },
            ],
        })
        
        # Definieer meetmomenten
        action_plan['meetmomenten'] = [
            {'week': 0, 'type': 'Baseline meting'},
            {'week': 4, 'type': 'Tussentijdse evaluatie'},
            {'week': 8, 'type': 'Mid-term evaluatie'},
            {'week': 12, 'type': 'Eind evaluatie'},
        ]
        
        # Definieer success criteria
        action_plan['success_criteria'] = [
            {
                'criterium': 'Vermindering geïsoleerde leden',
                'doel': 'Minder dan 10% geïsoleerde leden',
                'meetbaar': 'Aantal leden met <2 connecties',
            },
            {
                'criterium': 'Verbetering emotioneel welzijn',
                'doel': 'Gemiddelde score > 7.0',
                'meetbaar': 'Gemiddelde emotionele welzijn score',
            },
            {
                'criterium': 'Verhoging psychologische veiligheid',
                'doel': 'Minder dan 15% lage veiligheid scores',
                'meetbaar': 'Percentage relaties met veiligheid <4',
            },
            {
                'criterium': 'Versterking culturele cohesie',
                'doel': 'Fragmentatie < 0.2',
                'meetbaar': 'Fragmentatie metric',
            },
        ]
        
        return action_plan
    
    def generate_communication_plan(self) -> Dict[str, Any]:
        """
        Genereer een communicatieplan voor interventies.
        
        Returns:
            Dict met communicatie strategie
        """
        return {
            'doelgroepen': [
                {
                    'groep': 'Bestuur',
                    'boodschap': 'Strategische noodzaak van affectieve dynamiek voor ledenbehoud',
                    'kanaal': 'Bestuursvergadering, schriftelijk rapport',
                },
                {
                    'groep': 'Coaches en trainers',
                    'boodschap': 'Praktische tools voor versterken psychologische veiligheid',
                    'kanaal': 'Trainer bijeenkomst, workshop',
                },
                {
                    'groep': 'Leden en ouders',
                    'boodschap': 'Waarde van sociale verbondenheid en emotioneel welzijn',
                    'kanaal': 'Nieuwsbrief, informatieavond',
                },
                {
                    'groep': 'Vrijwilligers',
                    'boodschap': 'Hun rol in creëren van positief klimaat',
                    'kanaal': 'Vrijwilligers bijeenkomst',
                },
            ],
            'communicatie_principes': [
                'Transparantie over bevindingen',
                'Positieve framing (kansen, niet alleen problemen)',
                'Anonimiteit van individuele data',
                'Co-creatie van oplossingen',
                'Regelmatige updates over voortgang',
            ],
        }
