"""
Visualization: Visualisatie tools voor affectieve dynamiek

Dit module biedt visualisatie tools om de affectieve dynamiek
visueel inzichtelijk te maken.
"""

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from ..core.relationship_graph import RelationshipGraph
from ..core.affective_metrics import AffectiveMetrics


class NetworkVisualizer:
    """
    Visualisatie tools voor het relationship netwerk.
    """
    
    def __init__(self, relationship_graph: RelationshipGraph):
        """
        Initialiseer network visualizer.
        
        Args:
            relationship_graph: RelationshipGraph om te visualiseren
        """
        self.graph = relationship_graph
    
    def plot_network(
        self,
        color_by: str = 'emotionele_welzijn',
        size_by: str = 'centrality',
        layout: str = 'spring',
        figsize: Tuple[int, int] = (12, 8),
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Visualiseer het sociale netwerk.
        
        Args:
            color_by: Attribuut om nodes mee te kleuren
            size_by: Attribuut om node grootte mee te bepalen
            layout: Layout algoritme ('spring', 'circular', 'kamada_kawai')
            figsize: Figuur grootte
            save_path: Optioneel pad om figuur op te slaan
            
        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        if len(self.graph.graph) == 0:
            ax.text(
                0.5, 0.5, 
                'Geen data om te visualiseren',
                ha='center', va='center'
            )
            return fig
        
        # Bepaal layout
        if layout == 'spring':
            pos = nx.spring_layout(self.graph.graph, k=0.5, iterations=50)
        elif layout == 'circular':
            pos = nx.circular_layout(self.graph.graph)
        elif layout == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(self.graph.graph)
        else:
            pos = nx.spring_layout(self.graph.graph)
        
        # Bepaal node colors
        node_colors = self._get_node_colors(color_by)
        
        # Bepaal node sizes
        node_sizes = self._get_node_sizes(size_by)
        
        # Bepaal edge widths op basis van relatie sterkte
        edge_widths = []
        for u, v in self.graph.graph.edges():
            attrs = self.graph.get_relationship_attributes(u, v)
            width = attrs.get('sterkte', 5) / 2.0
            edge_widths.append(width)
        
        # Teken netwerk
        nx.draw_networkx_edges(
            self.graph.graph, pos,
            width=edge_widths,
            alpha=0.3,
            edge_color='gray',
            ax=ax
        )
        
        nodes = nx.draw_networkx_nodes(
            self.graph.graph, pos,
            node_color=node_colors,
            node_size=node_sizes,
            cmap=plt.cm.RdYlGn,
            vmin=0, vmax=10,
            ax=ax
        )
        
        # Voeg labels toe
        labels = {}
        for node in self.graph.graph.nodes():
            attrs = self.graph.get_member_attributes(node)
            labels[node] = attrs.get('naam', node)
        
        nx.draw_networkx_labels(
            self.graph.graph, pos,
            labels,
            font_size=8,
            ax=ax
        )
        
        # Voeg colorbar toe
        if color_by:
            plt.colorbar(
                nodes, 
                ax=ax, 
                label=color_by.replace('_', ' ').title()
            )
        
        ax.set_title(
            f'Sociaal Netwerk - Vereniging: {self.graph.get_metadata().get("naam_vereniging", "Onbekend")}',
            fontsize=14,
            fontweight='bold'
        )
        ax.axis('off')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def _get_node_colors(self, color_by: str) -> List[float]:
        """Bepaal node kleuren op basis van attribuut."""
        colors = []
        for node in self.graph.graph.nodes():
            attrs = self.graph.get_member_attributes(node)
            value = attrs.get(color_by, 5.0)
            colors.append(value)
        return colors
    
    def _get_node_sizes(self, size_by: str) -> List[float]:
        """Bepaal node groottes."""
        if size_by == 'centrality':
            centrality = self.graph.calculate_centrality_measures()
            sizes = []
            for node in self.graph.graph.nodes():
                size = centrality['degree'].get(node, 0) * 3000 + 100
                sizes.append(size)
            return sizes
        else:
            return [300] * len(self.graph.graph)
    
    def plot_communities(
        self,
        figsize: Tuple[int, int] = (12, 8),
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Visualiseer communities binnen het netwerk.
        
        Args:
            figsize: Figuur grootte
            save_path: Optioneel pad om figuur op te slaan
            
        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        if len(self.graph.graph) == 0:
            ax.text(
                0.5, 0.5,
                'Geen data om te visualiseren',
                ha='center', va='center'
            )
            return fig
        
        # Detecteer communities
        communities = self.graph.detect_communities()
        
        # Maak kleurmap voor communities
        colors = plt.cm.tab10(np.linspace(0, 1, len(communities)))
        
        # Assign colors to nodes
        node_colors = {}
        for idx, community in enumerate(communities):
            for node in community:
                node_colors[node] = colors[idx]
        
        # Layout
        pos = nx.spring_layout(self.graph.graph, k=0.5, iterations=50)
        
        # Teken per community
        for idx, community in enumerate(communities):
            subgraph = self.graph.graph.subgraph(community)
            nx.draw_networkx_nodes(
                subgraph, pos,
                node_color=[colors[idx]] * len(community),
                node_size=300,
                label=f'Community {idx+1} (n={len(community)})',
                ax=ax
            )
        
        # Teken edges
        nx.draw_networkx_edges(
            self.graph.graph, pos,
            alpha=0.2,
            edge_color='gray',
            ax=ax
        )
        
        # Labels
        labels = {}
        for node in self.graph.graph.nodes():
            attrs = self.graph.get_member_attributes(node)
            labels[node] = attrs.get('naam', node)
        
        nx.draw_networkx_labels(
            self.graph.graph, pos,
            labels,
            font_size=8,
            ax=ax
        )
        
        ax.set_title(
            f'Communities binnen Vereniging - {len(communities)} groepen gedetecteerd',
            fontsize=14,
            fontweight='bold'
        )
        ax.legend(loc='upper left')
        ax.axis('off')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig


class MetricsVisualizer:
    """
    Visualisatie tools voor affectieve metrieken.
    """
    
    def __init__(
        self,
        relationship_graph: RelationshipGraph,
        affective_metrics: Optional[AffectiveMetrics] = None
    ):
        """
        Initialiseer metrics visualizer.
        
        Args:
            relationship_graph: RelationshipGraph met data
            affective_metrics: Optioneel AffectiveMetrics object
        """
        self.graph = relationship_graph
        self.metrics = affective_metrics or AffectiveMetrics(relationship_graph)
    
    def plot_comprehensive_dashboard(
        self,
        figsize: Tuple[int, int] = (16, 12),
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Creëer een uitgebreid dashboard met alle metrieken.
        
        Args:
            figsize: Figuur grootte
            save_path: Optioneel pad om figuur op te slaan
            
        Returns:
            matplotlib Figure object
        """
        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Overall health scores
        ax1 = fig.add_subplot(gs[0, :])
        self._plot_overall_health(ax1)
        
        # Emotioneel klimaat
        ax2 = fig.add_subplot(gs[1, 0])
        self._plot_emotional_climate(ax2)
        
        # Relationele kwaliteit
        ax3 = fig.add_subplot(gs[1, 1])
        self._plot_relational_quality(ax3)
        
        # Psychologische veiligheid
        ax4 = fig.add_subplot(gs[1, 2])
        self._plot_psychological_safety(ax4)
        
        # Culturele cohesie
        ax5 = fig.add_subplot(gs[2, 0])
        self._plot_cultural_cohesion(ax5)
        
        # Risico analyse
        ax6 = fig.add_subplot(gs[2, 1])
        self._plot_risk_analysis(ax6)
        
        # Netwerk statistieken
        ax7 = fig.add_subplot(gs[2, 2])
        self._plot_network_stats(ax7)
        
        fig.suptitle(
            f'Affective Dynamiek Dashboard - {self.graph.get_metadata().get("naam_vereniging", "Vereniging")}',
            fontsize=16,
            fontweight='bold'
        )
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def _plot_overall_health(self, ax):
        """Plot overall health scores."""
        scores = self.metrics.calculate_comprehensive_score()
        
        categories = [
            'Emotioneel\nKlimaat',
            'Relationele\nKwaliteit',
            'Psychologische\nVeiligheid',
            'Culturele\nCohesie',
            'Totale\nGezondheid'
        ]
        
        values = [
            scores.get('emotioneel_klimaat_score', 0),
            scores.get('relationele_kwaliteit_score', 0),
            scores.get('psychologische_veiligheid_score', 0),
            scores.get('culturele_cohesie_score', 0),
            scores.get('totale_affectieve_gezondheid', 0),
        ]
        
        colors = ['red' if v < 4 else 'orange' if v < 7 else 'green' for v in values]
        
        bars = ax.bar(categories, values, color=colors, alpha=0.7)
        ax.axhline(y=7, color='green', linestyle='--', alpha=0.3, label='Goed (>7)')
        ax.axhline(y=4, color='red', linestyle='--', alpha=0.3, label='Risico (<4)')
        ax.set_ylim(0, 10)
        ax.set_ylabel('Score (0-10)')
        ax.set_title('Overall Affectieve Gezondheid Scores')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        # Voeg waarden toe boven balken
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2., height,
                f'{value:.1f}',
                ha='center', va='bottom'
            )
    
    def _plot_emotional_climate(self, ax):
        """Plot emotional climate metrics."""
        emotional = self.metrics.calculate_emotional_climate()
        
        ax.text(0.5, 0.9, 'Emotioneel Klimaat', ha='center', va='top',
                fontweight='bold', fontsize=12, transform=ax.transAxes)
        
        metrics_text = f"""
Gemiddeld Welzijn: {emotional['gemiddeld_welzijn']:.1f}/10
Spreiding: {emotional['spreiding_welzijn']:.1f}

Hoog welzijn (>7): {emotional['percentage_hoog_welzijn']:.0f}%
Laag welzijn (<4): {emotional['percentage_laag_welzijn']:.0f}%
        """
        
        ax.text(0.1, 0.5, metrics_text.strip(), ha='left', va='center',
                fontfamily='monospace', transform=ax.transAxes)
        
        ax.axis('off')
    
    def _plot_relational_quality(self, ax):
        """Plot relational quality metrics."""
        relational = self.metrics.calculate_relational_quality()
        
        ax.text(0.5, 0.9, 'Relationele Kwaliteit', ha='center', va='top',
                fontweight='bold', fontsize=12, transform=ax.transAxes)
        
        metrics_text = f"""
Gem. Sterkte: {relational.get('gemiddelde_relatie_sterkte', 0):.1f}/10
Gem. Vertrouwen: {relational.get('gemiddeld_vertrouwen', 0):.1f}/10
Gem. Steun: {relational.get('gemiddelde_emotionele_steun', 0):.1f}/10

Sterke relaties: {relational.get('percentage_sterke_relaties', 0):.0f}%
        """
        
        ax.text(0.1, 0.5, metrics_text.strip(), ha='left', va='center',
                fontfamily='monospace', transform=ax.transAxes)
        
        ax.axis('off')
    
    def _plot_psychological_safety(self, ax):
        """Plot psychological safety metrics."""
        safety = self.metrics.calculate_psychological_safety()
        
        ax.text(0.5, 0.9, 'Psychologische Veiligheid', ha='center', va='top',
                fontweight='bold', fontsize=12, transform=ax.transAxes)
        
        metrics_text = f"""
Gemiddelde: {safety['gemiddelde_psychologische_veiligheid']:.1f}/10

Hoge veiligheid: {safety['percentage_hoge_veiligheid']:.0f}%
Lage veiligheid: {safety['percentage_lage_veiligheid']:.0f}%
        """
        
        ax.text(0.1, 0.5, metrics_text.strip(), ha='left', va='center',
                fontfamily='monospace', transform=ax.transAxes)
        
        ax.axis('off')
    
    def _plot_cultural_cohesion(self, ax):
        """Plot cultural cohesion metrics."""
        cultural = self.metrics.calculate_cultural_cohesion()
        
        ax.text(0.5, 0.9, 'Culturele Cohesie', ha='center', va='top',
                fontweight='bold', fontsize=12, transform=ax.transAxes)
        
        metrics_text = f"""
Netwerk dichtheid: {cultural['netwerk_dichtheid']:.2f}
Gem. clustering: {cultural['gemiddelde_clustering']:.2f}
Modulariteit: {cultural.get('modulariteit', 0):.2f}
Fragmentatie: {cultural['fragmentatie']:.2f}
        """
        
        ax.text(0.1, 0.5, metrics_text.strip(), ha='left', va='center',
                fontfamily='monospace', transform=ax.transAxes)
        
        ax.axis('off')
    
    def _plot_risk_analysis(self, ax):
        """Plot risk analysis."""
        risks = self.metrics.calculate_dropout_risk_indicators()
        
        ax.text(0.5, 0.9, 'Uitval Risico Analyse', ha='center', va='top',
                fontweight='bold', fontsize=12, transform=ax.transAxes)
        
        metrics_text = f"""
Totaal risico leden: {risks['totaal_risico_leden']}

Laag welzijn: {len(risks['leden_met_laag_welzijn'])}
Geïsoleerd: {len(risks['geisoleerde_leden'])}
Zwakke relaties: {len(risks['leden_met_zwakke_relaties'])}
        """
        
        ax.text(0.1, 0.5, metrics_text.strip(), ha='left', va='center',
                fontfamily='monospace', transform=ax.transAxes)
        
        ax.axis('off')
    
    def _plot_network_stats(self, ax):
        """Plot network statistics."""
        stats = self.graph.get_graph_metrics()
        
        ax.text(0.5, 0.9, 'Netwerk Statistieken', ha='center', va='top',
                fontweight='bold', fontsize=12, transform=ax.transAxes)
        
        metrics_text = f"""
Aantal leden: {stats['aantal_leden']}
Aantal relaties: {stats['aantal_relaties']}
Gem. connecties: {stats.get('gemiddelde_graad', 0):.1f}

Verbonden: {'Ja' if stats.get('is_verbonden', False) else 'Nee'}
Componenten: {stats.get('aantal_componenten', 0)}
        """
        
        ax.text(0.1, 0.5, metrics_text.strip(), ha='left', va='center',
                fontfamily='monospace', transform=ax.transAxes)
        
        ax.axis('off')
