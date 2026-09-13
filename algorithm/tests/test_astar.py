import unittest

from algorithm.astar import (
    astar,
    calculate_route_distance,
    haversine_distance,
    heuristic,
)


class TestAStar(unittest.TestCase):

    def setUp(self):
        self.coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0010),
            3: (13.0020, 80.0000),
            4: (13.0030, 80.0010),
            5: (13.0040, 80.0000),
        }

        self.graph = {
            1: [
                {
                    "edge_id": "1-2",
                    "to": 2,
                    "distance_km": 1.0,
                    "travel_time_min": 2.0,
                },
                {
                    "edge_id": "1-3",
                    "to": 3,
                    "distance_km": 1.5,
                    "travel_time_min": 3.0,
                },
            ],
            2: [
                {
                    "edge_id": "2-4",
                    "to": 4,
                    "distance_km": 1.0,
                    "travel_time_min": 2.0,
                },
            ],
            3: [
                {
                    "edge_id": "3-4",
                    "to": 4,
                    "distance_km": 1.0,
                    "travel_time_min": 1.0,
                },
            ],
            4: [
                {
                    "edge_id": "4-5",
                    "to": 5,
                    "distance_km": 1.0,
                    "travel_time_min": 2.0,
                },
            ],
            5: [],
        }

    def test_haversine_distance(self):
        distance = haversine_distance(
            (13.0000, 80.0000),
            (13.0010, 80.0000),
        )

        self.assertGreater(distance, 0)
        self.assertLess(distance, 1.0)

    def test_heuristic_returns_time(self):
        value = heuristic(
            1,
            5,
            self.coordinates,
        )

        self.assertGreater(value, 0)

    def test_finds_fastest_route(self):
        result = astar(
            self.graph,
            self.coordinates,
            1,
            5,
        )

        self.assertIsNotNone(result)

        # Both routes have the same total travel time:
        #
        # 1 -> 2 -> 4 -> 5 = 2 + 2 + 2 = 6 minutes
        # 1 -> 3 -> 4 -> 5 = 3 + 1 + 2 = 6 minutes
        #
        # Therefore either route is a valid optimal result.
        self.assertIn(
            result["route"],
            [
                [1, 2, 4, 5],
                [1, 3, 4, 5],
            ],
        )

        self.assertAlmostEqual(
            result["travel_time_min"],
            6.0,
        )

        # The selected route must contain exactly three edges.
        self.assertEqual(
            len(result["edges"]),
            3,
        )

    def test_start_equals_goal(self):
        result = astar(
            self.graph,
            self.coordinates,
            1,
            1,
        )

        self.assertEqual(
            result["route"],
            [1],
        )

        self.assertEqual(
            result["distance_km"],
            0.0,
        )

        self.assertEqual(
            result["travel_time_min"],
            0.0,
        )

        self.assertEqual(
            result["edges"],
            [],
        )

    def test_no_route_returns_none(self):
        graph = {
            1: [
                {
                    "edge_id": "1-2",
                    "to": 2,
                    "distance_km": 1.0,
                    "travel_time_min": 2.0,
                }
            ],
            2: [],
            3: [],
        }

        result = astar(
            graph,
            self.coordinates,
            1,
            3,
        )

        self.assertIsNone(result)

    def test_disconnected_graph(self):
        graph = {
            1: [],
            2: [],
            3: [],
            4: [],
            5: [],
        }

        result = astar(
            graph,
            self.coordinates,
            1,
            5,
        )

        self.assertIsNone(result)

    def test_invalid_start_node(self):
        with self.assertRaises(ValueError):
            astar(
                self.graph,
                self.coordinates,
                999,
                5,
            )

    def test_invalid_goal_node(self):
        with self.assertRaises(ValueError):
            astar(
                self.graph,
                self.coordinates,
                1,
                999,
            )

    def test_missing_start_coordinates(self):
        coordinates = dict(self.coordinates)

        del coordinates[1]

        with self.assertRaises(ValueError):
            astar(
                self.graph,
                coordinates,
                1,
                5,
            )

    def test_missing_goal_coordinates(self):
        coordinates = dict(self.coordinates)

        del coordinates[5]

        with self.assertRaises(ValueError):
            astar(
                self.graph,
                coordinates,
                1,
                5,
            )

    def test_invalid_edge_travel_time(self):
        graph = {
            1: [
                {
                    "edge_id": "1-2",
                    "to": 2,
                    "distance_km": 1.0,
                    "travel_time_min": 0,
                }
            ],
            2: [],
        }

        coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0010),
        }

        with self.assertRaises(ValueError):
            astar(
                graph,
                coordinates,
                1,
                2,
            )

    def test_invalid_edge_distance(self):
        graph = {
            1: [
                {
                    "edge_id": "1-2",
                    "to": 2,
                    "distance_km": -1.0,
                    "travel_time_min": 2.0,
                }
            ],
            2: [],
        }

        coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0010),
        }

        with self.assertRaises(ValueError):
            astar(
                graph,
                coordinates,
                1,
                2,
            )

    def test_parallel_edges_are_supported(self):
        graph = {
            1: [
                {
                    "edge_id": "slow-road",
                    "to": 2,
                    "distance_km": 1.0,
                    "travel_time_min": 5.0,
                },
                {
                    "edge_id": "fast-road",
                    "to": 2,
                    "distance_km": 2.0,
                    "travel_time_min": 2.0,
                },
            ],
            2: [],
        }

        coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0010),
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

        self.assertAlmostEqual(
            result["travel_time_min"],
            2.0,
        )

        self.assertAlmostEqual(
            result["distance_km"],
            2.0,
        )

        self.assertEqual(
            result["edges"][0]["edge_id"],
            "fast-road",
        )

    def test_direction_is_respected(self):
        graph = {
            1: [
                {
                    "edge_id": "one-way",
                    "to": 2,
                    "distance_km": 1.0,
                    "travel_time_min": 2.0,
                }
            ],
            2: [],
        }

        coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0010),
        }

        result = astar(
            graph,
            coordinates,
            2,
            1,
        )

        self.assertIsNone(result)

    def test_route_distance_helper(self):
        distance = calculate_route_distance(
            [1, 2, 4, 5],
            self.graph,
        )

        # 1 -> 2 = 1 km
        # 2 -> 4 = 1 km
        # 4 -> 5 = 1 km
        #
        # Total = 3 km
        self.assertAlmostEqual(
            distance,
            3.0,
        )

    def test_dynamic_travel_time_changes_route(self):
        graph = {
            1: [
                {
                    "edge_id": "route-a",
                    "to": 2,
                    "distance_km": 1.0,
                    "travel_time_min": 2.0,
                },
                {
                    "edge_id": "route-b",
                    "to": 3,
                    "distance_km": 1.0,
                    "travel_time_min": 4.0,
                },
            ],
            2: [
                {
                    "edge_id": "route-a-end",
                    "to": 4,
                    "distance_km": 1.0,
                    "travel_time_min": 2.0,
                }
            ],
            3: [
                {
                    "edge_id": "route-b-end",
                    "to": 4,
                    "distance_km": 1.0,
                    "travel_time_min": 2.0,
                }
            ],
            4: [],
        }

        coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0010),
            3: (13.0020, 80.0000),
            4: (13.0030, 80.0010),
        }

        first_result = astar(
            graph,
            coordinates,
            1,
            4,
        )

        self.assertEqual(
            first_result["route"],
            [1, 2, 4],
        )

        self.assertAlmostEqual(
            first_result["travel_time_min"],
            4.0,
        )

        # Simulate traffic congestion on route A.
        graph[1][0]["travel_time_min"] = 10.0

        second_result = astar(
            graph,
            coordinates,
            1,
            4,
        )

        self.assertEqual(
            second_result["route"],
            [1, 3, 4],
        )

        self.assertAlmostEqual(
            second_result["travel_time_min"],
            6.0,
        )

    def test_result_distance_matches_selected_edges(self):
        result = astar(
            self.graph,
            self.coordinates,
            1,
            5,
        )

        self.assertIsNotNone(result)

        edge_distance = sum(
            edge["distance_km"]
            for edge in result["edges"]
        )

        self.assertAlmostEqual(
            result["distance_km"],
            edge_distance,
        )

    def test_result_time_matches_selected_edges(self):
        result = astar(
            self.graph,
            self.coordinates,
            1,
            5,
        )

        self.assertIsNotNone(result)

        edge_time = sum(
            edge["travel_time_min"]
            for edge in result["edges"]
        )

        self.assertAlmostEqual(
            result["travel_time_min"],
            edge_time,
        )


if __name__ == "__main__":
    unittest.main()