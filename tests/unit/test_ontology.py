import unittest
from reuseiq.ontology.ontology_manager import OntologyManager


class TestOntologyManager(unittest.TestCase):

    def setUp(self):
        self.mgr = OntologyManager()

    def test_load_and_statistics(self):
        stats = self.mgr.get_ontology_statistics()
        self.assertGreater(stats["classes"], 10)
        self.assertGreater(stats["object_properties"], 2)
        self.assertGreater(stats["data_properties"], 2)
        self.assertGreater(stats["individuals"], 0)
        self.assertGreater(stats["total_triples"], 30)

    def test_subclasses_hierarchy(self):
        device_subclasses = self.mgr.get_subclasses("ComputingDevice")
        self.assertIn("Laptop", device_subclasses)
        self.assertIn("DesktopComputer", device_subclasses)
        self.assertIn("Tablet", device_subclasses)

        action_subclasses = self.mgr.get_subclasses("AdvisoryAction")
        self.assertIn("RepairOption", action_subclasses)
        self.assertIn("RefurbishOption", action_subclasses)
        self.assertIn("ComponentRecoveryOption", action_subclasses)

    def test_components_for_lap104(self):
        components = self.mgr.get_components_for_device("Device_LAP104")
        self.assertGreaterEqual(len(components), 2)
        comp_names = [c["name"] for c in components]
        self.assertIn("RAM_LAP104", comp_names)
        self.assertIn("Storage_LAP104", comp_names)

    def test_sparql_query(self):
        query = """
        PREFIX ewaste: <http://www.semanticweb.org/reuseiq/ontologies/2026/ewaste#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?device ?label WHERE {
            ?device a ewaste:Laptop ;
                    rdfs:label ?label .
        }
        """
        results = self.mgr.query_sparql(query)
        self.assertTrue(len(results) >= 1)
        self.assertIn("LAP104", results[0]["label"])


if __name__ == "__main__":
    unittest.main()
