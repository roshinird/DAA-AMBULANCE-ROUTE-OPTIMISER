import unittest

from algorithm.astar import astar


class TestAStarRobustness(unittest.TestCase):

    def test_dead_end_goal_is_reachable(self):
        """
        A valid destination does not need outgoing roads.

        Route:
            1 -> 2 -> 3

        Node 3 is the destination and has no outgoing edges.
        """

        graph = {
            1: [
                {
                    "edge_id": 1,
                    "to": 2,
                    "distance_km": 1.0,
                    "travel_time_min": 2.0,
                }
            ],
            2: [
                {
                    "edge_id": 2,
                    "to": 3,
                    "distance_km": 1.0,
                    "travel_time_min": 3.0,
                }
            ],
        }

        coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0000),
            3: (13.0020, 80.0000),
        }

        result = astar(
            graph,
            coordinates,
            1,
            3,
        )

        self.assertIsNotNone(result)

        self.assertEqual(
            result["route"],
            [1, 2, 3],
        )

        self.assertEqual(
            result["travel_time_min"],
            5.0,
        )

        self.assertEqual(
            result["distance_km"],
            2.0,
        )

    def test_dead_end_branch_does_not_confuse_search(self):
        """
        A dead-end branch should not prevent A* from finding
        another valid route.

            1 -> 2 -> 99       dead end

            1 -> 3 -> 4        goal
        """

        graph = {
            1: [
                {
                    "edge_id": 1,
                    "to": 2,
                    "distance_km": 1.0,
                    "travel_time_min": 1.0,
                },
                {
                    "edge_id": 2,
                    "to": 3,
                    "distance_km": 1.0,
                    "travel_time_min": 2.0,
                },
            ],
            2: [
                {
                    "edge_id": 3,
                    "to": 99,
                    "distance_km": 1.0,
                    "travel_time_min": 1.0,
                }
            ],
            3: [
                {
                    "edge_id": 4,
                    "to": 4,
                    "distance_km": 1.0,
                    "travel_time_min": 2.0,
                }
            ],
            99: [],
            4: [],
        }

        coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0000),
            3: (13.0000, 80.0010),
            4: (13.0000, 80.0020),
            99: (13.0030, 80.0000),
        }

        result = astar(
            graph,
            coordinates,
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
            4.0,
        )

    def test_unreachable_goal_returns_none(self):
        """
        A completely disconnected destination should return None.
        """

        graph = {
            1: [
                {
                    "edge_id": 1,
                    "to": 2,
                    "distance_km": 1.0,
                    "travel_time_min": 1.0,
                }
            ],
            2: [],
            3: [],
        }

        coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0000),
            3: (13.0100, 80.0100),
        }

        result = astar(
            graph,
            coordinates,
            1,
            3,
        )

        self.assertIsNone(result)

    def test_missing_destination_graph_key_is_valid(self):
        """
        The goal can exist only in coordinates and as the destination
        of an incoming edge.
        """

        graph = {
            1: [
                {
                    "edge_id": 1,
                    "to": 2,
                    "distance_km": 0.5,
                    "travel_time_min": 1.0,
                }
            ]
        }

        coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0000),
        }

        result = astar(
            graph,
            coordinates,
            1,
            2,
        )

        self.assertIsNotNone(result)

        self.assertEqual(
            result["route"],
            [1, 2],
        )

        self.assertEqual(
            result["travel_time_min"],
            1.0,
        )

    def test_parallel_edges_choose_fastest_edge(self):
        """
        Two physical road segments connect the same nodes.

        A* must choose the faster edge while preserving its exact
        edge identity.
        """

        graph = {
            1: [
                {
                    "edge_id": 101,
                    "to": 2,
                    "distance_km": 5.0,
                    "travel_time_min": 10.0,
                },
                {
                    "edge_id": 102,
                    "to": 2,
                    "distance_km": 3.0,
                    "travel_time_min": 4.0,
                },
            ],
            2: [],
        }

        coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0020, 80.0000),
        }

        result = astar(
            graph,
            coordinates,
            1,
            2,
        )

        self.assertIsNotNone(result)

        self.assertEqual(
            result["route"],
            [1, 2],
        )

        self.assertEqual(
            len(result["edges"]),
            1,
        )

        self.assertEqual(
            result["edges"][0]["edge_id"],
            102,
        )

        self.assertEqual(
            result["distance_km"],
            3.0,
        )

        self.assertEqual(
            result["travel_time_min"],
            4.0,
        )

    def test_direction_is_never_reversed(self):
        """
        A directed road 1 -> 2 must not automatically become 2 -> 1.
        """

        graph = {
            1: [
                {
                    "edge_id": 1,
                    "to": 2,
                    "distance_km": 1.0,
                    "travel_time_min": 2.0,
                }
            ],
            2: [],
        }

        coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0000),
        }

        result = astar(
            graph,
            coordinates,
            2,
            1,
        )

        self.assertIsNone(result)

    def test_zero_travel_time_is_rejected(self):
        """
        Zero-cost road traversal is invalid for this routing model.
        """

        graph = {
            1: [
                {
                    "edge_id": 1,
                    "to": 2,
                    "distance_km": 1.0,
                    "travel_time_min": 0.0,
                }
            ],
            2: [],
        }

        coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0000),
        }

        with self.assertRaises(ValueError):
            astar(
                graph,
                coordinates,
                1,
                2,
            )

    def test_negative_travel_time_is_rejected(self):
        """
        Negative travel time must never be accepted.
        """

        graph = {
            1: [
                {
                    "edge_id": 1,
                    "to": 2,
                    "distance_km": 1.0,
                    "travel_time_min": -2.0,
                }
            ],
            2: [],
        }

        coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0000),
        }

        with self.assertRaises(ValueError):
            astar(
                graph,
                coordinates,
                1,
                2,
            )

    def test_negative_distance_is_rejected(self):
        """
        Negative road distance is invalid.
        """

        graph = {
            1: [
                {
                    "edge_id": 1,
                    "to": 2,
                    "distance_km": -1.0,
                    "travel_time_min": 2.0,
                }
            ],
            2: [],
        }

        coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0000),
        }

        with self.assertRaises(ValueError):
            astar(
                graph,
                coordinates,
                1,
                2,
            )

    def test_nan_travel_time_is_rejected(self):
        """
        NaN must never enter the routing cost calculation.
        """

        graph = {
            1: [
                {
                    "edge_id": 1,
                    "to": 2,
                    "distance_km": 1.0,
                    "travel_time_min": float("nan"),
                }
            ],
            2: [],
        }

        coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0000),
        }

        with self.assertRaises(ValueError):
            astar(
                graph,
                coordinates,
                1,
                2,
            )

    def test_infinite_travel_time_is_rejected(self):
        """
        Infinite travel time must never enter the routing calculation.
        """

        graph = {
            1: [
                {
                    "edge_id": 1,
                    "to": 2,
                    "distance_km": 1.0,
                    "travel_time_min": float("inf"),
                }
            ],
            2: [],
        }

        coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0000),
        }

        with self.assertRaises(ValueError):
            astar(
                graph,
                coordinates,
                1,
                2,
            )

    def test_graph_is_not_modified(self):
        """
        Running A* must not mutate the routing graph.
        """

        graph = {
            1: [
                {
                    "edge_id": 1,
                    "to": 2,
                    "distance_km": 1.0,
                    "travel_time_min": 2.0,
                }
            ],
            2: [],
        }

        coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0000),
        }

        original_edge = dict(graph[1][0])

        astar(
            graph,
            coordinates,
            1,
            2,
        )

        self.assertEqual(
            graph[1][0],
            original_edge,
        )

    def test_repeated_routing_is_stable(self):
        """
        Running the same route repeatedly should produce the same
        result and should not accumulate state between executions.
        """

        graph = {
            1: [
                {
                    "edge_id": 1,
                    "to": 2,
                    "distance_km": 1.0,
                    "travel_time_min": 2.0,
                },
                {
                    "edge_id": 2,
                    "to": 3,
                    "distance_km": 1.0,
                    "travel_time_min": 3.0,
                },
            ],
            2: [
                {
                    "edge_id": 3,
                    "to": 4,
                    "distance_km": 1.0,
                    "travel_time_min": 2.0,
                }
            ],
            3: [
                {
                    "edge_id": 4,
                    "to": 4,
                    "distance_km": 1.0,
                    "travel_time_min": 3.0,
                }
            ],
            4: [],
        }

        coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0000),
            3: (13.0000, 80.0010),
            4: (13.0020, 80.0000),
        }

        first_result = astar(
            graph,
            coordinates,
            1,
            4,
        )

        second_result = astar(
            graph,
            coordinates,
            1,
            4,
        )

        self.assertEqual(
            first_result["route"],
            second_result["route"],
        )

        self.assertEqual(
            first_result["distance_km"],
            second_result["distance_km"],
        )

        self.assertEqual(
            first_result["travel_time_min"],
            second_result["travel_time_min"],
        )

        self.assertEqual(
            first_result["edges"],
            second_result["edges"],
        )


if __name__ == "__main__":
    unittest.main()
