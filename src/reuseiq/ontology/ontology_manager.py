"""
ReUseIQ - Ontology Manager

Loads and queries the formal OWL/RDF e-waste domain ontology using RDFLib,
providing semantic classification, hierarchy navigation, and SPARQL querying.
"""

import os
from typing import Any, Dict, List, Optional
import rdflib
from rdflib.namespace import OWL, RDF, RDFS, XSD


class OntologyManager:
    """Manages RDFLib interactions with the e-waste OWL ontology."""

    DEFAULT_BASE_URI = "http://www.semanticweb.org/reuseiq/ontologies/2026/ewaste#"

    def __init__(self, owl_path: Optional[str] = None):
        if owl_path is None:
            curr_dir = os.path.dirname(os.path.abspath(__file__))
            self.owl_path = os.path.join(curr_dir, "ewaste_ontology.owl")
        else:
            self.owl_path = owl_path

        self.graph = rdflib.Graph()
        self.ns = rdflib.Namespace(self.DEFAULT_BASE_URI)
        self.load_ontology()

    def load_ontology(self) -> None:
        """Parses the OWL XML file into an RDFLib graph."""
        if not os.path.exists(self.owl_path):
            raise FileNotFoundError(f"Ontology file not found at {self.owl_path}")
        self.graph.parse(self.owl_path, format="xml")

    def get_classes(self) -> List[Dict[str, str]]:
        """Returns all OWL classes defined in the ontology with their labels."""
        results = []
        for s in self.graph.subjects(RDF.type, OWL.Class):
            # Extract local name
            uri_str = str(s)
            local_name = uri_str.split("#")[-1] if "#" in uri_str else uri_str.split("/")[-1]
            label = self.graph.value(s, RDFS.label)
            label_str = str(label) if label else local_name
            results.append({
                "uri": uri_str,
                "name": local_name,
                "label": label_str
            })
        return sorted(results, key=lambda x: x["name"])

    def get_subclasses(self, class_name: str) -> List[str]:
        """Returns immediate subclasses of a given class."""
        parent_uri = self.ns[class_name]
        subclasses = []
        for s in self.graph.subjects(RDFS.subClassOf, parent_uri):
            uri_str = str(s)
            local_name = uri_str.split("#")[-1] if "#" in uri_str else uri_str.split("/")[-1]
            subclasses.append(local_name)
        return sorted(subclasses)

    def get_components_for_device(self, device_individual_name: str) -> List[Dict[str, Any]]:
        """Queries components linked to a specific device individual."""
        dev_uri = self.ns[device_individual_name]
        has_component_prop = self.ns["hasComponent"]
        components = []

        for comp_uri in self.graph.objects(dev_uri, has_component_prop):
            comp_local = str(comp_uri).split("#")[-1]
            comp_type = self.graph.value(comp_uri, RDF.type)
            type_local = str(comp_type).split("#")[-1] if comp_type else "Component"
            is_working = self.graph.value(comp_uri, self.ns["isWorking"])
            is_working_bool = bool(is_working) if is_working is not None else False
            label = self.graph.value(comp_uri, RDFS.label)

            components.append({
                "uri": str(comp_uri),
                "name": comp_local,
                "type": type_local,
                "label": str(label) if label else comp_local,
                "is_working": is_working_bool
            })
        return components

    def query_sparql(self, query_string: str) -> List[Dict[str, str]]:
        """Executes a custom SPARQL query over the e-waste graph."""
        res = self.graph.query(query_string)
        output = []
        for row in res:
            row_dict = {}
            for var in res.vars:
                val = row[var]
                row_dict[str(var)] = str(val) if val is not None else ""
            output.append(row_dict)
        return output

    def get_ontology_statistics(self) -> Dict[str, int]:
        """Returns count of classes, properties, individuals, and triples."""
        classes_count = len(list(self.graph.subjects(RDF.type, OWL.Class)))
        obj_props = len(list(self.graph.subjects(RDF.type, OWL.ObjectProperty)))
        data_props = len(list(self.graph.subjects(RDF.type, OWL.DatatypeProperty)))
        individuals = len(list(self.graph.subjects(RDF.type, OWL.NamedIndividual)))
        total_triples = len(self.graph)

        return {
            "classes": classes_count,
            "object_properties": obj_props,
            "data_properties": data_props,
            "individuals": individuals,
            "total_triples": total_triples
        }
