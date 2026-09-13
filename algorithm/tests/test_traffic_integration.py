import unittest

from algorithm.astar import astar
from algorithm.traffic import apply_traffic_weights


class TestTrafficIntegration(unittest.TestCase):

    def setUp(self):
        """
        Create a small routing graph with two possible routes.

        Route A:
            1 -> 2 -> 4
            Base time = 2 + 2 = 4 minutes

        Route B:
            1 -> 3 -> 4
            Base time = 3 + 3 = 6 minutes

        Without traffic, A* should choose Route A.
        """

        self.coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0000),
            3: (13.0000, 80.0010),
            4: (13.0020, 80.0000),
        }

        self.graph = {
            1: [
                {
                    "edge_id": 1,
                    "to": 2,
                    "distance_km": 1.0,
                    "travel_time_min": 2.0,
                    "base_travel_time_min": 2.0,
                },
                {
                    "edge_id": 2,
                    "to": 3,
                    "distance_km": 1.0,
                    "travel_time_min": 3.0,
                    "base_travel_time_min": 3.0,
                },
            ],
            2: [
                {
                    "edge_id": 3,
                    "to": 4,
                    "distance_km": 1.0,
                    "travel_time_min": 2.0,
                    "base_travel_time_min": 2.0,
                }
            ],
            3: [
                {
                    "edge_id": 4,
                    "to": 4,
                    "distance_km": 1.0,
                    "travel_time_min": 3.0,
                    "base_travel_time_min": 3.0,
                }
            ],
            4: [],
        }

    def test_normal_traffic_uses_fastest_route(self):
        """
        Under normal traffic:

            Route A = 4 minutes
            Route B = 6 minutes

        Therefore A* should choose 1 -> 2 -> 4.
        """

        weighted_graph = apply_traffic_weights(
            self.graph
        )

        result = astar(
            weighted_graph,
            self.coordinates,
            1,
            4,
        )

        self.assertIsNotNone(result)

        self.assertEqual(
            result["route"],
            [1, 2, 4],
        )

        self.assertEqual(
            result["travel_time_min"],
            4.0,
        )

    def test_heavy_traffic_changes_route(self):
        """
        Heavy traffic is applied to Route A.

        Route A:

            2 + 2 = 4 minutes
            4 × 2.0 = 8 minutes

        Route B:

            3 + 3 = 6 minutes

        Therefore A* should switch to Route B.
        """

        weighted_graph = apply_traffic_weights(
            self.graph,
            {
                1: 2.0,
                3: 2.0,
            },
        )

        result = astar(
            weighted_graph,
            self.coordinates,
            1,
            4,
        )

        self.assertIsNotNone(result)

        self.assertEqual(
            result["route"],
            [1, 3, 4],
        )

        self.assertEqual(
            result["travel_time_min"],
            6.0,
        )

    def test_traffic_changes_route_without_modifying_base_graph(self):
        """
        Applying traffic must not modify the original graph.
        """

        apply_traffic_weights(
            self.graph,
            {
                1: 3.0,
                3: 3.0,
            },
        )

        self.assertEqual(
            self.graph[1][0]["travel_time_min"],
            2.0,
        )

        self.assertEqual(
            self.graph[2][0]["travel_time_min"],
            2.0,
        )

    def test_severe_traffic_makes_alternative_route_preferred(self):
        """
        Severe traffic on Route A should make Route B preferable.
        """

        weighted_graph = apply_traffic_weights(
            self.graph,
            {
                1: 3.0,
                3: 3.0,
            },
        )

        result = astar(
            weighted_graph,
            self.coordinates,
            1,
            4,
        )

        self.assertIsNotNone(result)

        self.assertEqual(
            result["route"],
            [1, 3, 4],
        )

        self.assertEqual(
            result["travel_time_min"],
            6.0,
        )


if __name__ == "__main__":
    unittest.main()