"""
Unit tests voor RelationshipGraph
"""

import unittest
import sys
sys.path.insert(0, '../src')

from graaf_zeppelin.core.relationship_graph import RelationshipGraph


class TestRelationshipGraph(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.graph = RelationshipGraph()
    
    def test_initialization(self):
        """Test graph initialization."""
        self.assertEqual(len(self.graph.graph), 0)
        self.assertEqual(self.graph.graph.number_of_edges(), 0)
    
    def test_add_member(self):
        """Test adding a member."""
        self.graph.add_member("lid_001", naam="Jan", rol="speler", leeftijd=25)
        self.assertIn("lid_001", self.graph.graph)
        
        attrs = self.graph.get_member_attributes("lid_001")
        self.assertEqual(attrs['naam'], "Jan")
        self.assertEqual(attrs['rol'], "speler")
        self.assertEqual(attrs['leeftijd'], 25)
    
    def test_add_relationship(self):
        """Test adding a relationship."""
        self.graph.add_member("lid_001", naam="Jan")
        self.graph.add_member("lid_002", naam="Sara")
        
        self.graph.add_relationship(
            "lid_001", "lid_002",
            sterkte=8.0, vertrouwen=9.0
        )
        
        self.assertTrue(self.graph.graph.has_edge("lid_001", "lid_002"))
        
        attrs = self.graph.get_relationship_attributes("lid_001", "lid_002")
        self.assertEqual(attrs['sterkte'], 8.0)
        self.assertEqual(attrs['vertrouwen'], 9.0)
    
    def test_get_neighbors(self):
        """Test getting neighbors of a member."""
        self.graph.add_member("lid_001", naam="Jan")
        self.graph.add_member("lid_002", naam="Sara")
        self.graph.add_member("lid_003", naam="Tim")
        
        self.graph.add_relationship("lid_001", "lid_002", sterkte=8.0)
        self.graph.add_relationship("lid_001", "lid_003", sterkte=7.0)
        
        neighbors = self.graph.get_neighbors("lid_001")
        self.assertEqual(len(neighbors), 2)
        self.assertIn("lid_002", neighbors)
        self.assertIn("lid_003", neighbors)
    
    def test_identify_isolated_members(self):
        """Test identifying isolated members."""
        # Add members
        for i in range(5):
            self.graph.add_member(f"lid_{i:03d}", naam=f"Lid {i}")
        
        # Add relationships (lid_000 and lid_001 have connections)
        self.graph.add_relationship("lid_000", "lid_001", sterkte=8.0)
        self.graph.add_relationship("lid_001", "lid_002", sterkte=7.0)
        
        # lid_003 and lid_004 have no connections
        isolated = self.graph.identify_isolated_members(threshold=1)
        self.assertIn("lid_003", isolated)
        self.assertIn("lid_004", isolated)
    
    def test_calculate_centrality_measures(self):
        """Test centrality calculations."""
        # Create a simple network
        for i in range(4):
            self.graph.add_member(f"lid_{i:03d}", naam=f"Lid {i}")
        
        self.graph.add_relationship("lid_000", "lid_001", sterkte=8.0)
        self.graph.add_relationship("lid_001", "lid_002", sterkte=7.0)
        self.graph.add_relationship("lid_002", "lid_003", sterkte=6.0)
        
        centrality = self.graph.calculate_centrality_measures()
        
        self.assertIn('degree', centrality)
        self.assertIn('betweenness', centrality)
        self.assertIn('closeness', centrality)
        self.assertIn('eigenvector', centrality)
        
        # lid_001 and lid_002 should have higher centrality (middle of chain)
        self.assertGreater(
            centrality['betweenness']['lid_001'],
            centrality['betweenness']['lid_000']
        )
    
    def test_detect_communities(self):
        """Test community detection."""
        # Create two separate groups
        # Group 1
        for i in range(3):
            self.graph.add_member(f"group1_{i}", naam=f"G1 Lid {i}")
        self.graph.add_relationship("group1_0", "group1_1", sterkte=8.0)
        self.graph.add_relationship("group1_1", "group1_2", sterkte=8.0)
        
        # Group 2
        for i in range(3):
            self.graph.add_member(f"group2_{i}", naam=f"G2 Lid {i}")
        self.graph.add_relationship("group2_0", "group2_1", sterkte=8.0)
        self.graph.add_relationship("group2_1", "group2_2", sterkte=8.0)
        
        # Connect groups weakly
        self.graph.add_relationship("group1_0", "group2_0", sterkte=3.0)
        
        communities = self.graph.detect_communities()
        self.assertGreaterEqual(len(communities), 1)
    
    def test_get_graph_metrics(self):
        """Test graph metrics calculation."""
        # Add some members and relationships
        for i in range(5):
            self.graph.add_member(f"lid_{i:03d}", naam=f"Lid {i}")
        
        self.graph.add_relationship("lid_000", "lid_001", sterkte=8.0)
        self.graph.add_relationship("lid_001", "lid_002", sterkte=7.0)
        self.graph.add_relationship("lid_002", "lid_003", sterkte=6.0)
        self.graph.add_relationship("lid_003", "lid_004", sterkte=5.0)
        
        metrics = self.graph.get_graph_metrics()
        
        self.assertEqual(metrics['aantal_leden'], 5)
        self.assertEqual(metrics['aantal_relaties'], 4)
        self.assertIn('gemiddelde_graad', metrics)
        self.assertIn('dichtheid', metrics)
        self.assertIn('gemiddelde_clustering', metrics)
    
    def test_export_import(self):
        """Test exporting and importing graph."""
        # Create a graph
        self.graph.add_member("lid_001", naam="Jan", rol="speler")
        self.graph.add_member("lid_002", naam="Sara", rol="coach")
        self.graph.add_relationship("lid_001", "lid_002", sterkte=8.0)
        self.graph.set_metadata(naam_vereniging="Test Vereniging")
        
        # Export
        data = self.graph.export_to_dict()
        
        # Import into new graph
        new_graph = RelationshipGraph.from_dict(data)
        
        # Verify
        self.assertEqual(len(new_graph.graph), 2)
        self.assertEqual(new_graph.graph.number_of_edges(), 1)
        self.assertEqual(
            new_graph.get_metadata()['naam_vereniging'],
            "Test Vereniging"
        )


if __name__ == '__main__':
    unittest.main()
