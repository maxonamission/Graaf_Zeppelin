"""
Unit tests voor AffectiveMetrics
"""

import unittest
import sys
sys.path.insert(0, '../src')

from graaf_zeppelin.core.relationship_graph import RelationshipGraph
from graaf_zeppelin.core.affective_metrics import AffectiveMetrics


class TestAffectiveMetrics(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures with a sample graph."""
        self.graph = RelationshipGraph()
        
        # Add members with varying emotional wellbeing
        self.graph.add_member("lid_001", naam="Jan", emotionele_welzijn=8.0)
        self.graph.add_member("lid_002", naam="Sara", emotionele_welzijn=7.5)
        self.graph.add_member("lid_003", naam="Tim", emotionele_welzijn=3.0)  # Low
        self.graph.add_member("lid_004", naam="Emma", emotionele_welzijn=8.5)
        self.graph.add_member("lid_005", naam="Max", emotionele_welzijn=3.5)  # Low
        
        # Add relationships with varying quality
        self.graph.add_relationship(
            "lid_001", "lid_002",
            sterkte=8.0, vertrouwen=9.0,
            emotionele_steun=8.5, psychologische_veiligheid=8.0
        )
        self.graph.add_relationship(
            "lid_002", "lid_004",
            sterkte=9.0, vertrouwen=8.5,
            emotionele_steun=9.0, psychologische_veiligheid=8.5
        )
        self.graph.add_relationship(
            "lid_002", "lid_003",
            sterkte=5.0, vertrouwen=6.0,
            emotionele_steun=5.5, psychologische_veiligheid=6.0
        )  # Weak relationship
        
        self.metrics = AffectiveMetrics(self.graph)
    
    def test_calculate_emotional_climate(self):
        """Test emotional climate calculation."""
        emotional = self.metrics.calculate_emotional_climate()
        
        self.assertIn('gemiddeld_welzijn', emotional)
        self.assertIn('spreiding_welzijn', emotional)
        self.assertIn('percentage_hoog_welzijn', emotional)
        self.assertIn('percentage_laag_welzijn', emotional)
        
        # Check that values are in expected ranges
        self.assertGreater(emotional['gemiddeld_welzijn'], 0)
        self.assertLess(emotional['gemiddeld_welzijn'], 10)
        
        # We have 2 low wellbeing members out of 5 (40%)
        self.assertGreater(emotional['percentage_laag_welzijn'], 0)
    
    def test_calculate_relational_quality(self):
        """Test relational quality calculation."""
        relational = self.metrics.calculate_relational_quality()
        
        self.assertIn('gemiddelde_relatie_sterkte', relational)
        self.assertIn('gemiddeld_vertrouwen', relational)
        self.assertIn('gemiddelde_emotionele_steun', relational)
        self.assertIn('percentage_sterke_relaties', relational)
        
        # Check that values are in expected ranges
        self.assertGreater(relational['gemiddelde_relatie_sterkte'], 0)
        self.assertLess(relational['gemiddelde_relatie_sterkte'], 10)
    
    def test_calculate_psychological_safety(self):
        """Test psychological safety calculation."""
        safety = self.metrics.calculate_psychological_safety()
        
        self.assertIn('gemiddelde_psychologische_veiligheid', safety)
        self.assertIn('percentage_hoge_veiligheid', safety)
        self.assertIn('percentage_lage_veiligheid', safety)
        
        # Check that values are in expected ranges
        self.assertGreaterEqual(safety['gemiddelde_psychologische_veiligheid'], 0)
        self.assertLessEqual(safety['gemiddelde_psychologische_veiligheid'], 10)
    
    def test_calculate_cultural_cohesion(self):
        """Test cultural cohesion calculation."""
        cultural = self.metrics.calculate_cultural_cohesion()
        
        self.assertIn('netwerk_dichtheid', cultural)
        self.assertIn('gemiddelde_clustering', cultural)
        self.assertIn('modulariteit', cultural)
        self.assertIn('fragmentatie', cultural)
        
        # Network density should be between 0 and 1
        self.assertGreaterEqual(cultural['netwerk_dichtheid'], 0)
        self.assertLessEqual(cultural['netwerk_dichtheid'], 1)
    
    def test_calculate_dropout_risk_indicators(self):
        """Test dropout risk indicator calculation."""
        risks = self.metrics.calculate_dropout_risk_indicators()
        
        self.assertIn('leden_met_laag_welzijn', risks)
        self.assertIn('geisoleerde_leden', risks)
        self.assertIn('leden_met_zwakke_relaties', risks)
        self.assertIn('totaal_risico_leden', risks)
        
        # We should identify lid_003 and lid_005 with low wellbeing
        self.assertEqual(len(risks['leden_met_laag_welzijn']), 2)
        self.assertIn('lid_003', risks['leden_met_laag_welzijn'])
        self.assertIn('lid_005', risks['leden_met_laag_welzijn'])
        
        # Total risk members should be at least as many as low wellbeing
        self.assertGreaterEqual(risks['totaal_risico_leden'], 2)
    
    def test_calculate_comprehensive_score(self):
        """Test comprehensive score calculation."""
        scores = self.metrics.calculate_comprehensive_score()
        
        self.assertIn('emotioneel_klimaat_score', scores)
        self.assertIn('relationele_kwaliteit_score', scores)
        self.assertIn('psychologische_veiligheid_score', scores)
        self.assertIn('culturele_cohesie_score', scores)
        self.assertIn('totale_affectieve_gezondheid', scores)
        
        # All scores should be between 0 and 10
        for key, value in scores.items():
            self.assertGreaterEqual(value, 0, f"{key} should be >= 0")
            self.assertLessEqual(value, 10, f"{key} should be <= 10")
    
    def test_empty_graph(self):
        """Test metrics with empty graph."""
        empty_graph = RelationshipGraph()
        empty_metrics = AffectiveMetrics(empty_graph)
        
        emotional = empty_metrics.calculate_emotional_climate()
        self.assertEqual(emotional['gemiddeld_welzijn'], 0.0)
        
        comprehensive = empty_metrics.calculate_comprehensive_score()
        self.assertEqual(comprehensive['totale_affectieve_gezondheid'], 0.0)


if __name__ == '__main__':
    unittest.main()
