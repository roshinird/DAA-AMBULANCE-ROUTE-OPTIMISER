import unittest

from algorithm.graph_adapter import Edge
from algorithm.route_engine import (
    build_normalized_graph,
)


class TestBuildNormalizedGraph(unittest.TestCase):

    def test_edge_conversion(self):
        edge = Edge(
            edge_id=10,
            from_node=1,
            to_node=2,
            distance_m=500.0,
            road_type="primary",
            road_name="Test Road",
            oneway=True,
            base_travel_time_min=0.75,
        )

        graph = {
            1: [edge]
        }

        normalized = build_normalized_graph(graph)

        self.assertIn(1, normalized)
        self.assertEqual(len(normalized[1]), 1)

        converted = normalized[1][0]

        self.assertEqual(converted["edge_id"], 10)
        self.assertEqual(converted["to"], 2)
        self.assertEqual(converted["distance_km"], 0.5)
        self.assertEqual(
            converted["travel_time_min"],
            0.75,
        )
        self.assertEqual(
            converted["road_type"],
            "primary",
        )
        self.assertEqual(
            converted["road_name"],
            "Test Road",
        )
        self.assertTrue(converted["oneway"])

    def test_parallel_edges_are_preserved(self):
        edge1 = Edge(
            edge_id=1,
            from_node=1,
            to_node=2,
            distance_m=500.0,
            road_type="primary",
            road_name="Road A",
            oneway=True,
            base_travel_time_min=0.75,
        )

        edge2 = Edge(
            edge_id=2,
            from_node=1,
            to_node=2,
            distance_m=800.0,
            road_type="secondary",
            road_name="Road B",
            oneway=True,
            base_travel_time_min=1.2,
        )

        graph = {
            1: [edge1, edge2]
        }

        normalized = build_normalized_graph(graph)

        self.assertEqual(
            len(normalized[1]),
            2,
        )

        self.assertEqual(
            normalized[1][0]["edge_id"],
            1,
        )

        self.assertEqual(
            normalized[1][1]["edge_id"],
            2,
        )

    def test_distance_is_converted_from_meters_to_kilometres(self):
        edge = Edge(
            edge_id=5,
            from_node=10,
            to_node=20,
            distance_m=1250.0,
            road_type="residential",
            road_name="Test Street",
            oneway=False,
            base_travel_time_min=1.875,
        )

        normalized = build_normalized_graph(
            {
                10: [edge]
            }
        )

        self.assertEqual(
            normalized[10][0]["distance_km"],
            1.25,
        )

    def test_original_edge_is_not_modified(self):
        edge = Edge(
            edge_id=7,
            from_node=3,
            to_node=4,
            distance_m=1000.0,
            road_type="tertiary",
            road_name="Original Road",
            oneway=False,
            base_travel_time_min=1.5,
        )

        original_values = (
            edge.edge_id,
            edge.from_node,
            edge.to_node,
            edge.distance_m,
            edge.road_type,
            edge.road_name,
            edge.oneway,
            edge.base_travel_time_min,
        )

        build_normalized_graph(
            {
                3: [edge]
            }
        )

        self.assertEqual(
            (
                edge.edge_id,
                edge.from_node,
                edge.to_node,
                edge.distance_m,
                edge.road_type,
                edge.road_name,
                edge.oneway,
                edge.base_travel_time_min,
            ),
            original_values,
        )

    def test_multiple_source_nodes_are_preserved(self):
        edge1 = Edge(
            edge_id=1,
            from_node=1,
            to_node=2,
            distance_m=100.0,
            road_type="residential",
            road_name="Road A",
            oneway=False,
            base_travel_time_min=0.15,
        )

        edge2 = Edge(
            edge_id=2,
            from_node=3,
            to_node=4,
            distance_m=200.0,
            road_type="primary",
            road_name="Road B",
            oneway=True,
            base_travel_time_min=0.3,
        )

        graph = {
            1: [edge1],
            3: [edge2],
        }

        normalized = build_normalized_graph(graph)

        self.assertEqual(
            set(normalized.keys()),
            {1, 3},
        )

        self.assertEqual(
            normalized[1][0]["to"],
            2,
        )

        self.assertEqual(
            normalized[3][0]["to"],
            4,
        )


if __name__ == "__main__":
    unittest.main()