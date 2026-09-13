import unittest
from pathlib import Path

from algorithm.graph_adapter import (
    DEFAULT_SPEED_KMH,
    distance_to_travel_time,
    load_edges,
    load_nodes,
    load_osm_graph,
)


class TestGraphAdapter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.project_root = Path(__file__).resolve().parents[2]

        cls.nodes_path = (
            cls.project_root
            / "data"
            / "nodes.csv"
        )

        cls.edges_path = (
            cls.project_root
            / "data"
            / "edges.csv"
        )

    def test_distance_to_travel_time(self):
        # 1 km at 60 km/h = 1 minute
        result = distance_to_travel_time(
            1000,
            60,
        )

        self.assertAlmostEqual(
            result,
            1.0,
            places=6,
        )

    def test_load_nodes(self):
        # This test requires the OSM data to exist locally.
        if not self.nodes_path.exists():
            self.skipTest(
                "Local data/nodes.csv is not available yet."
            )

        coordinates = load_nodes(
            self.nodes_path
        )

        self.assertGreater(
            len(coordinates),
            0,
        )

        self.assertIn(
            30037862,
            coordinates,
        )

        latitude, longitude = coordinates[
            30037862
        ]

        self.assertAlmostEqual(
            latitude,
            13.0109201,
        )

        self.assertAlmostEqual(
            longitude,
            80.2170576,
        )

    def test_load_edges(self):
        if not self.edges_path.exists():
            self.skipTest(
                "Local data/edges.csv is not available yet."
            )

        graph, edges = load_edges(
            self.edges_path
        )

        self.assertGreater(
            len(edges),
            0,
        )

        self.assertGreater(
            len(graph),
            0,
        )

        first_edge = edges[0]

        self.assertEqual(
            first_edge.from_node,
            30037862,
        )

        self.assertEqual(
            first_edge.to_node,
            30037863,
        )

        self.assertGreater(
            first_edge.distance_m,
            0,
        )

        self.assertGreater(
            first_edge.base_travel_time_min,
            0,
        )

    def test_duplicate_edges_are_preserved(self):
        if not self.edges_path.exists():
            self.skipTest(
                "Local data/edges.csv is not available yet."
            )

        graph, edges = load_edges(
            self.edges_path
        )

        duplicate_edges = [
            edge
            for edge in edges
            if (
                edge.from_node == 243325994
                and edge.to_node == 2407565892
            )
        ]

        self.assertEqual(
            len(duplicate_edges),
            2,
        )

    def test_default_speed(self):
        self.assertEqual(
            DEFAULT_SPEED_KMH,
            40.0,
        )

    def test_complete_osm_loader(self):
        if not (
            self.nodes_path.exists()
            and self.edges_path.exists()
        ):
            self.skipTest(
                "Local OSM CSV files are not available yet."
            )

        graph, coordinates, edges = load_osm_graph(
            self.nodes_path,
            self.edges_path,
        )

        self.assertGreater(
            len(coordinates),
            0,
        )

        self.assertGreater(
            len(graph),
            0,
        )

        self.assertGreater(
            len(edges),
            0,
        )

        for edge in edges[:20]:
            self.assertIn(
                edge.from_node,
                coordinates,
            )

            self.assertIn(
                edge.to_node,
                coordinates,
            )


if __name__ == "__main__":
    unittest.main()