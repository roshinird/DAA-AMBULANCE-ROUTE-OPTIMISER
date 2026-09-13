import unittest

from algorithm.route_engine import RouteEngine


NODES_PATH = "data/nodes.csv"
EDGES_PATH = "data/edges.csv"

START_NODE = 30037862
GOAL_NODE = 30037875


class TestRouteEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = RouteEngine(
            nodes_path=NODES_PATH,
            edges_path=EDGES_PATH,
        )

    def test_osm_graph_is_loaded(self):

        self.assertEqual(
            self.engine.get_node_count(),
            5491,
        )

        self.assertEqual(
            self.engine.get_edge_count(),
            13475,
        )

    def test_get_node_coordinates(self):

        coordinates = (
            self.engine.get_node_coordinates(
                START_NODE
            )
        )

        self.assertEqual(
            len(coordinates),
            2,
        )

        self.assertAlmostEqual(
            coordinates[0],
            13.0109201,
        )

        self.assertAlmostEqual(
            coordinates[1],
            80.2170576,
        )

    def test_real_osm_route(self):

        result = self.engine.find_route(
            START_NODE,
            GOAL_NODE,
        )

        self.assertIsNotNone(result)

        self.assertIn(
            "route",
            result,
        )

        self.assertIn(
            "distance_km",
            result,
        )

        self.assertIn(
            "travel_time_min",
            result,
        )

        self.assertGreater(
            len(result["route"]),
            1,
        )

        self.assertGreater(
            result["distance_km"],
            0,
        )

        self.assertGreater(
            result["travel_time_min"],
            0,
        )

        self.assertEqual(
            result["route"][0],
            START_NODE,
        )

        self.assertEqual(
            result["route"][-1],
            GOAL_NODE,
        )

    def test_real_osm_route_matches_expected_distance(self):

        result = self.engine.find_route(
            START_NODE,
            GOAL_NODE,
        )

        self.assertIsNotNone(result)

        self.assertAlmostEqual(
            result["distance_km"],
            3.059215587385447,
            places=10,
        )

    def test_real_osm_route_matches_expected_time(self):

        result = self.engine.find_route(
            START_NODE,
            GOAL_NODE,
        )

        self.assertIsNotNone(result)

        self.assertAlmostEqual(
            result["travel_time_min"],
            4.5888233810781704,
            places=10,
        )

    def test_start_equals_goal(self):

        result = self.engine.find_route(
            START_NODE,
            START_NODE,
        )

        self.assertIsNotNone(result)

        self.assertEqual(
            result["route"],
            [START_NODE],
        )

        self.assertEqual(
            result["distance_km"],
            0.0,
        )

        self.assertEqual(
            result["travel_time_min"],
            0.0,
        )

    def test_unreachable_node_returns_none(self):

        # 999999999 is intentionally not present
        # in the real OSM node dataset.

        with self.assertRaises(KeyError):

            self.engine.find_route(
                START_NODE,
                999999999,
            )

    def test_traffic_multipliers_are_forwarded_to_astar(self):

        normal = self.engine.find_route(
            START_NODE,
            GOAL_NODE,
        )

        self.assertIsNotNone(normal)

        # Apply heavy traffic to every edge used by the
        # normal route.
        route_edge_ids = [
            edge.edge_id
            for edge in self.engine.find_route_result(
                START_NODE,
                GOAL_NODE,
            ).edges
        ]

        traffic = {
            edge_id: 3.0
            for edge_id in route_edge_ids
        }

        congested = self.engine.find_route(
            START_NODE,
            GOAL_NODE,
            traffic_multipliers=traffic,
        )

        self.assertIsNotNone(congested)

        self.assertGreater(
            congested["travel_time_min"],
            normal["travel_time_min"],
        )

    def test_route_result_can_return_selected_edges(self):

        result = self.engine.find_route_result(
            START_NODE,
            GOAL_NODE,
        )

        self.assertIsNotNone(result)

        self.assertGreater(
            len(result.edges),
            0,
        )

        self.assertEqual(
            len(result.edges),
            len(result.route) - 1,
        )


if __name__ == "__main__":
    unittest.main()