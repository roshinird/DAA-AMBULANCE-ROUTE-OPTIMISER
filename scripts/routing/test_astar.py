import json
import unittest

from scripts.routing.astar import (
    TRAFFIC_MULTIPLIERS,
    a_star,
    load_graph,
    reroute,
    route_is_valid,
)


class TestAStarRouting(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.nodes, cls.graph = load_graph()

        with open(
            "data/locations/locations.json",
            "r",
            encoding="utf-8"
        ) as file:
            cls.locations = json.load(file)

        cls.patients = ["P1", "P2", "P3"]
        cls.hospitals = ["H1", "H2"]

    def node(self, location):
        return self.locations[location]["graph_node_id"]

    def test_six_patient_hospital_routes_are_reachable(self):
        for patient in self.patients:
            for hospital in self.hospitals:
                with self.subTest(patient=patient, hospital=hospital):
                    path, travel_time = a_star(
                        self.graph,
                        self.nodes,
                        self.node(patient),
                        self.node(hospital),
                    )

                    self.assertIsNotNone(path)
                    self.assertGreater(len(path), 1)
                    self.assertGreater(travel_time, 0)
                    self.assertTrue(
                        route_is_valid(self.graph, path)
                    )

    def test_traffic_conditions_change_route_cost(self):
        start = self.node("P1")
        goal = self.node("H2")

        normal_path, normal_time = a_star(
            self.graph,
            self.nodes,
            start,
            goal,
        )

        first_edge = (normal_path[0], normal_path[1])

        heavy_path, heavy_time = a_star(
            self.graph,
            self.nodes,
            start,
            goal,
            traffic_conditions={
                first_edge: "heavy"
            },
        )

        self.assertIsNotNone(heavy_path)
        self.assertGreaterEqual(heavy_time, normal_time)
        self.assertTrue(
            route_is_valid(self.graph, heavy_path)
        )

    def test_blocked_edge_triggers_rerouting(self):
        start = self.node("P1")
        goal = self.node("H2")

        original_path, original_time = a_star(
            self.graph,
            self.nodes,
            start,
            goal,
        )

        blocked_edge = (original_path[0], original_path[1])

        rerouted_path, rerouted_time = a_star(
            self.graph,
            self.nodes,
            start,
            goal,
            blocked_edges={blocked_edge},
        )

        self.assertIsNotNone(rerouted_path)
        self.assertNotEqual(original_path, rerouted_path)
        self.assertGreaterEqual(rerouted_time, original_time)
        self.assertNotIn(blocked_edge, zip(
            rerouted_path,
            rerouted_path[1:]
        ))
        self.assertTrue(
            route_is_valid(
                self.graph,
                rerouted_path,
                blocked_edges={blocked_edge},
            )
        )

    def test_dedicated_reroute_function(self):
        start = self.node("P1")
        goal = self.node("H2")

        original_path, original_time = a_star(
            self.graph,
            self.nodes,
            start,
            goal,
        )

        blocked_edge = (original_path[0], original_path[1])

        rerouted_path, rerouted_time = reroute(
            self.graph,
            self.nodes,
            start,
            goal,
            blocked_edges={blocked_edge},
        )

        self.assertIsNotNone(rerouted_path)
        self.assertNotEqual(original_path, rerouted_path)
        self.assertGreaterEqual(rerouted_time, original_time)
        self.assertTrue(
            route_is_valid(
                self.graph,
                rerouted_path,
                blocked_edges={blocked_edge},
            )
        )

    def test_route_is_invalid_when_edge_is_blocked(self):
        start = self.node("P1")
        goal = self.node("H2")

        path, _ = a_star(
            self.graph,
            self.nodes,
            start,
            goal,
        )

        first_edge = (path[0], path[1])

        self.assertFalse(
            route_is_valid(
                self.graph,
                path,
                blocked_edges={first_edge},
            )
        )

    def test_invalid_start_node_raises_error(self):
        with self.assertRaises(ValueError):
            a_star(
                self.graph,
                self.nodes,
                "INVALID_START",
                self.node("H1"),
            )

    def test_invalid_goal_node_raises_error(self):
        with self.assertRaises(ValueError):
            a_star(
                self.graph,
                self.nodes,
                self.node("P1"),
                "INVALID_GOAL",
            )

    def test_fully_blocked_route_becomes_unreachable(self):
        start = self.node("P1")
        goal = self.node("H2")

        path, _ = a_star(
            self.graph,
            self.nodes,
            start,
            goal,
        )

        all_route_edges = set(
            zip(path, path[1:])
        )

        blocked_path, blocked_time = a_star(
            self.graph,
            self.nodes,
            start,
            goal,
            blocked_edges=all_route_edges,
        )

        self.assertIsNone(blocked_path)
        self.assertEqual(blocked_time, float("inf"))

    def test_traffic_multiplier_values_are_defined(self):
        self.assertEqual(TRAFFIC_MULTIPLIERS["normal"], 1.0)
        self.assertGreater(
            TRAFFIC_MULTIPLIERS["light"],
            TRAFFIC_MULTIPLIERS["normal"],
        )
        self.assertGreater(
            TRAFFIC_MULTIPLIERS["moderate"],
            TRAFFIC_MULTIPLIERS["light"],
        )
        self.assertGreater(
            TRAFFIC_MULTIPLIERS["heavy"],
            TRAFFIC_MULTIPLIERS["moderate"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
