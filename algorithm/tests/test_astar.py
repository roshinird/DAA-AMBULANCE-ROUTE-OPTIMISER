import math
import unittest

from algorithm.astar import (
    MAX_AMBULANCE_SPEED_KMH,
    RouteResult,
    astar,
    haversine_distance_km,
    heuristic_time_minutes,
)
from algorithm.graph_adapter import Edge


def make_edge(
    edge_id,
    from_node,
    to_node,
    distance_m,
    travel_time_min,
):
    """
    Helper for creating test edges without depending on CSV files.
    """

    return Edge(
        edge_id=edge_id,
        from_node=from_node,
        to_node=to_node,
        distance_m=distance_m,
        road_type="test",
        road_name=f"Road {edge_id}",
        oneway=True,
        base_travel_time_min=travel_time_min,
    )


class TestHaversine(unittest.TestCase):

    def test_same_coordinate_is_zero(self):
        coordinate = (13.0109, 80.2170)

        distance = haversine_distance_km(
            coordinate,
            coordinate,
        )

        self.assertAlmostEqual(
            distance,
            0.0,
            places=10,
        )

    def test_known_distance_is_reasonable(self):
        chennai = (
            13.0827,
            80.2707,
        )

        nearby_location = (
            13.0927,
            80.2807,
        )

        distance = haversine_distance_km(
            chennai,
            nearby_location,
        )

        self.assertGreater(
            distance,
            0.0,
        )

        self.assertLess(
            distance,
            2.0,
        )

    def test_invalid_coordinate_is_rejected(self):
        with self.assertRaises(ValueError):
            haversine_distance_km(
                (100.0, 80.0),
                (13.0, 80.0),
            )


class TestHeuristic(unittest.TestCase):

    def setUp(self):
        self.coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0100, 80.0100),
        }

    def test_heuristic_is_zero_at_goal(self):
        result = heuristic_time_minutes(
            2,
            2,
            self.coordinates,
        )

        self.assertAlmostEqual(
            result,
            0.0,
            places=10,
        )

    def test_heuristic_is_positive_for_different_nodes(self):
        result = heuristic_time_minutes(
            1,
            2,
            self.coordinates,
        )

        self.assertGreater(
            result,
            0.0,
        )

    def test_faster_max_speed_reduces_heuristic(self):
        slow_estimate = heuristic_time_minutes(
            1,
            2,
            self.coordinates,
            max_speed_kmh=60.0,
        )

        fast_estimate = heuristic_time_minutes(
            1,
            2,
            self.coordinates,
            max_speed_kmh=120.0,
        )

        self.assertGreater(
            slow_estimate,
            fast_estimate,
        )

    def test_invalid_max_speed_is_rejected(self):
        with self.assertRaises(ValueError):
            heuristic_time_minutes(
                1,
                2,
                self.coordinates,
                max_speed_kmh=0,
            )


class TestAStarBasic(unittest.TestCase):

    def setUp(self):

        self.coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0010),
            3: (13.0010, 80.0020),
            4: (13.0020, 80.0030),
            5: (13.0030, 80.0040),
        }

    def test_finds_fastest_route(self):

        edge_1 = make_edge(
            1,
            1,
            2,
            100,
            2.0,
        )

        edge_2 = make_edge(
            2,
            2,
            5,
            100,
            2.0,
        )

        edge_3 = make_edge(
            3,
            1,
            3,
            100,
            1.0,
        )

        edge_4 = make_edge(
            4,
            3,
            4,
            100,
            1.0,
        )

        edge_5 = make_edge(
            5,
            4,
            5,
            100,
            1.0,
        )

        graph = {
            1: [edge_1, edge_3],
            2: [edge_2],
            3: [edge_4],
            4: [edge_5],
        }

        result = astar(
            graph,
            self.coordinates,
            1,
            5,
        )

        self.assertIsNotNone(result)

        self.assertEqual(
            result.route,
            [1, 3, 4, 5],
        )

        self.assertEqual(
            [edge.edge_id for edge in result.edges],
            [3, 4, 5],
        )

        self.assertAlmostEqual(
            result.distance_km,
            0.3,
            places=10,
        )

        self.assertAlmostEqual(
            result.travel_time_min,
            3.0,
            places=10,
        )

    def test_start_equals_goal(self):

        graph = {}

        result = astar(
            graph,
            self.coordinates,
            1,
            1,
        )

        self.assertIsNotNone(result)

        self.assertEqual(
            result.route,
            [1],
        )

        self.assertEqual(
            result.edges,
            [],
        )

        self.assertEqual(
            result.distance_km,
            0.0,
        )

        self.assertEqual(
            result.travel_time_min,
            0.0,
        )

    def test_unreachable_goal_returns_none(self):

        edge = make_edge(
            1,
            1,
            2,
            100,
            2.0,
        )

        graph = {
            1: [edge],
        }

        result = astar(
            graph,
            self.coordinates,
            1,
            5,
        )

        self.assertIsNone(result)

    def test_dead_end_goal_can_be_reached(self):

        edge_1 = make_edge(
            1,
            1,
            2,
            100,
            2.0,
        )

        edge_2 = make_edge(
            2,
            2,
            5,
            100,
            3.0,
        )

        graph = {
            1: [edge_1],
            2: [edge_2],
        }

        result = astar(
            graph,
            self.coordinates,
            1,
            5,
        )

        self.assertIsNotNone(result)

        self.assertEqual(
            result.route,
            [1, 2, 5],
        )

    def test_directed_graph_is_respected(self):

        edge = make_edge(
            1,
            1,
            2,
            100,
            2.0,
        )

        graph = {
            1: [edge],
        }

        result_forward = astar(
            graph,
            self.coordinates,
            1,
            2,
        )

        result_reverse = astar(
            graph,
            self.coordinates,
            2,
            1,
        )

        self.assertIsNotNone(
            result_forward
        )

        self.assertIsNone(
            result_reverse
        )


class TestParallelEdges(unittest.TestCase):

    def test_parallel_edges_are_preserved(self):

        slow_edge = make_edge(
            10,
            1,
            2,
            500,
            8.0,
        )

        fast_edge = make_edge(
            11,
            1,
            2,
            300,
            3.0,
        )

        final_edge = make_edge(
            12,
            2,
            3,
            200,
            2.0,
        )

        coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0010),
            3: (13.0020, 80.0020),
        }

        graph = {
            1: [
                slow_edge,
                fast_edge,
            ],
            2: [
                final_edge,
            ],
        }

        result = astar(
            graph,
            coordinates,
            1,
            3,
        )

        self.assertIsNotNone(result)

        self.assertEqual(
            result.route,
            [1, 2, 3],
        )

        self.assertEqual(
            [edge.edge_id for edge in result.edges],
            [11, 12],
        )

        self.assertAlmostEqual(
            result.travel_time_min,
            5.0,
        )


class TestTrafficRerouting(unittest.TestCase):

    def setUp(self):

        self.coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0010),
            3: (13.0010, 80.0020),
            4: (13.0020, 80.0030),
        }

    def test_traffic_can_change_selected_route(self):

        # Route A:
        #
        # 1 -> 2 -> 4
        #
        # Normal = 2 + 2 = 4 minutes

        edge_a1 = make_edge(
            1,
            1,
            2,
            100,
            2.0,
        )

        edge_a2 = make_edge(
            2,
            2,
            4,
            100,
            2.0,
        )

        # Route B:
        #
        # 1 -> 3 -> 4
        #
        # Normal = 3 + 3 = 6 minutes

        edge_b1 = make_edge(
            3,
            1,
            3,
            100,
            3.0,
        )

        edge_b2 = make_edge(
            4,
            3,
            4,
            100,
            3.0,
        )

        graph = {
            1: [
                edge_a1,
                edge_b1,
            ],
            2: [
                edge_a2,
            ],
            3: [
                edge_b2,
            ],
        }

        normal_result = astar(
            graph,
            self.coordinates,
            1,
            4,
        )

        self.assertEqual(
            normal_result.route,
            [1, 2, 4],
        )

        # Make Route A heavily congested.
        traffic = {
            1: 3.0,
            2: 3.0,
        }

        traffic_result = astar(
            graph,
            self.coordinates,
            1,
            4,
            traffic_multipliers=traffic,
        )

        self.assertEqual(
            traffic_result.route,
            [1, 3, 4],
        )

        self.assertAlmostEqual(
            traffic_result.travel_time_min,
            6.0,
        )

    def test_missing_traffic_multiplier_means_normal(self):

        edge = make_edge(
            1,
            1,
            2,
            100,
            5.0,
        )

        graph = {
            1: [edge],
        }

        coordinates = {
            1: (13.0, 80.0),
            2: (13.001, 80.001),
        }

        result = astar(
            graph,
            coordinates,
            1,
            2,
            traffic_multipliers={},
        )

        self.assertAlmostEqual(
            result.travel_time_min,
            5.0,
        )


class TestGraphIntegrity(unittest.TestCase):

    def test_astar_does_not_modify_graph(self):

        edge_1 = make_edge(
            1,
            1,
            2,
            100,
            2.0,
        )

        edge_2 = make_edge(
            2,
            2,
            3,
            100,
            2.0,
        )

        graph = {
            1: [edge_1],
            2: [edge_2],
        }

        coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0010),
            3: (13.0020, 80.0020),
        }

        original_graph = {
            node: list(edges)
            for node, edges in graph.items()
        }

        astar(
            graph,
            coordinates,
            1,
            3,
        )

        self.assertEqual(
            graph,
            original_graph,
        )

    def test_edge_objects_are_returned_exactly(self):

        edge_1 = make_edge(
            1,
            1,
            2,
            100,
            2.0,
        )

        edge_2 = make_edge(
            2,
            2,
            3,
            100,
            2.0,
        )

        graph = {
            1: [edge_1],
            2: [edge_2],
        }

        coordinates = {
            1: (13.0, 80.0),
            2: (13.001, 80.001),
            3: (13.002, 80.002),
        }

        result = astar(
            graph,
            coordinates,
            1,
            3,
        )

        self.assertIs(
            result.edges[0],
            edge_1,
        )

        self.assertIs(
            result.edges[1],
            edge_2,
        )


class TestValidation(unittest.TestCase):

    def setUp(self):

        self.coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0010),
        }

        self.edge = make_edge(
            1,
            1,
            2,
            100,
            2.0,
        )

        self.graph = {
            1: [self.edge],
        }

    def test_unknown_start_node(self):

        with self.assertRaises(KeyError):
            astar(
                self.graph,
                self.coordinates,
                999,
                2,
            )

    def test_unknown_goal_node(self):

        with self.assertRaises(KeyError):
            astar(
                self.graph,
                self.coordinates,
                1,
                999,
            )

    def test_zero_traffic_multiplier_is_rejected(self):

        with self.assertRaises(ValueError):
            astar(
                self.graph,
                self.coordinates,
                1,
                2,
                traffic_multipliers={
                    1: 0.0,
                },
            )

    def test_negative_traffic_multiplier_is_rejected(self):

        with self.assertRaises(ValueError):
            astar(
                self.graph,
                self.coordinates,
                1,
                2,
                traffic_multipliers={
                    1: -1.0,
                },
            )

    def test_nan_traffic_multiplier_is_rejected(self):

        with self.assertRaises(ValueError):
            astar(
                self.graph,
                self.coordinates,
                1,
                2,
                traffic_multipliers={
                    1: math.nan,
                },
            )

    def test_infinite_traffic_multiplier_is_rejected(self):

        with self.assertRaises(ValueError):
            astar(
                self.graph,
                self.coordinates,
                1,
                2,
                traffic_multipliers={
                    1: math.inf,
                },
            )

    def test_invalid_max_speed_is_rejected(self):

        with self.assertRaises(ValueError):
            astar(
                self.graph,
                self.coordinates,
                1,
                2,
                max_ambulance_speed_kmh=0,
            )

    def test_non_dictionary_traffic_data_is_rejected(self):

        with self.assertRaises(TypeError):
            astar(
                self.graph,
                self.coordinates,
                1,
                2,
                traffic_multipliers=[],
            )


class TestRepeatedRouting(unittest.TestCase):

    def test_repeated_routes_are_identical(self):

        edge_1 = make_edge(
            1,
            1,
            2,
            100,
            2.0,
        )

        edge_2 = make_edge(
            2,
            2,
            3,
            100,
            3.0,
        )

        graph = {
            1: [edge_1],
            2: [edge_2],
        }

        coordinates = {
            1: (13.0000, 80.0000),
            2: (13.0010, 80.0010),
            3: (13.0020, 80.0020),
        }

        first = astar(
            graph,
            coordinates,
            1,
            3,
        )

        second = astar(
            graph,
            coordinates,
            1,
            3,
        )

        self.assertEqual(
            first,
            second,
        )


class TestResultType(unittest.TestCase):

    def test_result_is_route_result(self):

        edge = make_edge(
            1,
            1,
            2,
            100,
            2.0,
        )

        graph = {
            1: [edge],
        }

        coordinates = {
            1: (13.0, 80.0),
            2: (13.001, 80.001),
        }

        result = astar(
            graph,
            coordinates,
            1,
            2,
        )

        self.assertIsInstance(
            result,
            RouteResult,
        )


class TestConstants(unittest.TestCase):

    def test_max_ambulance_speed_is_positive(self):

        self.assertGreater(
            MAX_AMBULANCE_SPEED_KMH,
            0,
        )


if __name__ == "__main__":
    unittest.main()