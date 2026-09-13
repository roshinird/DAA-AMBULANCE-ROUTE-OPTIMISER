import unittest

from algorithm.astar import astar
from algorithm.graph_adapter import Edge
from algorithm.traffic_adapter import normalize_traffic_multipliers


class TestTrafficAwareRouting(unittest.TestCase):

    def setUp(self):
        # Synthetic graph created only for testing the Member-2
        # traffic-aware routing behavior.
        #
        # Route A:
        # 1 -> 2 -> 4
        #
        # Route B:
        # 1 -> 3 -> 4
        #
        # Under normal traffic, Route A is faster.
        # Under heavy traffic on Route A, A* should choose Route B.

        self.coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0000),
            3: (13.0000, 80.0020),
            4: (13.0010, 80.0020),
        }

        edge_a1 = Edge(
            edge_id=101,
            from_node=1,
            to_node=2,
            distance_m=100.0,
            road_type="primary",
            road_name="Route A - First Road",
            oneway=True,
            base_travel_time_min=1.0,
        )

        edge_a2 = Edge(
            edge_id=102,
            from_node=2,
            to_node=4,
            distance_m=100.0,
            road_type="primary",
            road_name="Route A - Second Road",
            oneway=True,
            base_travel_time_min=1.0,
        )

        edge_b1 = Edge(
            edge_id=201,
            from_node=1,
            to_node=3,
            distance_m=150.0,
            road_type="secondary",
            road_name="Route B - First Road",
            oneway=True,
            base_travel_time_min=1.5,
        )

        edge_b2 = Edge(
            edge_id=202,
            from_node=3,
            to_node=4,
            distance_m=150.0,
            road_type="secondary",
            road_name="Route B - Second Road",
            oneway=True,
            base_travel_time_min=1.5,
        )

        self.graph = {
            1: [edge_a1, edge_b1],
            2: [edge_a2],
            3: [edge_b2],
            4: [],
        }

    def test_normal_traffic_selects_fastest_route(self):
        traffic = normalize_traffic_multipliers(
            {
                101: 1.0,
                102: 1.0,
                201: 1.0,
                202: 1.0,
            }
        )

        result = astar(
            self.graph,
            self.coordinates,
            1,
            4,
            traffic_multipliers=traffic,
        )

        self.assertIsNotNone(result)
        self.assertEqual(
            result.route,
            [1, 2, 4],
        )

        self.assertEqual(
            result.distance_km,
            0.2,
        )

        self.assertEqual(
            result.travel_time_min,
            2.0,
        )

    def test_heavy_traffic_reroutes_to_alternative(self):
        traffic = normalize_traffic_multipliers(
            {
                101: 3.0,
                102: 3.0,
                201: 1.0,
                202: 1.0,
            }
        )

        result = astar(
            self.graph,
            self.coordinates,
            1,
            4,
            traffic_multipliers=traffic,
        )

        self.assertIsNotNone(result)
        self.assertEqual(
            result.route,
            [1, 3, 4],
        )

        self.assertEqual(
            result.distance_km,
            0.3,
        )

        self.assertEqual(
            result.travel_time_min,
            3.0,
        )

    def test_partial_traffic_data_uses_normal_traffic_for_missing_edges(self):
        traffic = normalize_traffic_multipliers(
            {
                101: 1.0,
                102: 1.0,
            }
        )

        result = astar(
            self.graph,
            self.coordinates,
            1,
            4,
            traffic_multipliers=traffic,
        )

        self.assertIsNotNone(result)
        self.assertEqual(
            result.route,
            [1, 2, 4],
        )

        self.assertEqual(
            result.travel_time_min,
            2.0,
        )

    def test_traffic_does_not_modify_graph(self):
        original_graph = {
            node: list(edges)
            for node, edges in self.graph.items()
        }

        traffic = normalize_traffic_multipliers(
            {
                101: 4.0,
                102: 4.0,
                201: 1.0,
                202: 1.0,
            }
        )

        result = astar(
            self.graph,
            self.coordinates,
            1,
            4,
            traffic_multipliers=traffic,
        )

        self.assertIsNotNone(result)

        self.assertEqual(
            self.graph,
            original_graph,
        )

    def test_zero_traffic_multiplier_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize_traffic_multipliers(
                {
                    101: 0.0,
                }
            )

    def test_negative_traffic_multiplier_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize_traffic_multipliers(
                {
                    101: -1.0,
                }
            )


if __name__ == "__main__":
    unittest.main()