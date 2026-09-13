"""
Tests for the Member 2 OSM graph adapter.

These tests validate:
    - Node loading
    - Edge loading
    - Travel-time calculation
    - CSV validation
    - Coordinate validation
    - Distance validation
    - Speed validation
    - Duplicate node detection
    - Missing-node detection
    - Parallel-edge preservation
    - Self-loop preservation
    - Real Member 1 OSM dataset integration
"""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from algorithm.graph_adapter import (
    DEFAULT_SPEED_KMH,
    distance_to_travel_time,
    load_edges,
    load_nodes,
    load_osm_graph,
    validate_graph_nodes,
)


class TestDistanceToTravelTime(unittest.TestCase):
    """Tests for distance-to-time conversion."""

    def test_one_kilometer_at_40_kmh(self):
        result = distance_to_travel_time(
            1000,
            40,
        )

        self.assertAlmostEqual(
            result,
            1.5,
        )

    def test_invalid_distance_zero(self):
        with self.assertRaises(ValueError):
            distance_to_travel_time(
                0,
                40,
            )

    def test_invalid_distance_negative(self):
        with self.assertRaises(ValueError):
            distance_to_travel_time(
                -100,
                40,
            )

    def test_invalid_speed_zero(self):
        with self.assertRaises(ValueError):
            distance_to_travel_time(
                1000,
                0,
            )

    def test_invalid_speed_negative(self):
        with self.assertRaises(ValueError):
            distance_to_travel_time(
                1000,
                -40,
            )


class TestLoadNodes(unittest.TestCase):
    """Tests for OSM node loading."""

    def create_nodes_csv(
        self,
        directory: str,
        rows: list[dict[str, str]],
        columns=None,
    ) -> Path:
        """Create a temporary nodes CSV."""

        path = Path(directory) / "nodes.csv"

        if columns is None:
            columns = [
                "id",
                "latitude",
                "longitude",
            ]

        with path.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=columns,
            )

            writer.writeheader()
            writer.writerows(rows)

        return path

    def test_load_valid_nodes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.create_nodes_csv(
                directory,
                [
                    {
                        "id": "1",
                        "latitude": "13.0109",
                        "longitude": "80.2170",
                    },
                    {
                        "id": "2",
                        "latitude": "13.0123",
                        "longitude": "80.2210",
                    },
                ],
            )

            nodes = load_nodes(path)

            self.assertEqual(
                len(nodes),
                2,
            )

            self.assertEqual(
                nodes[1],
                (
                    13.0109,
                    80.2170,
                ),
            )

    def test_missing_nodes_file(self):
        with self.assertRaises(FileNotFoundError):
            load_nodes(
                "does_not_exist.csv"
            )

    def test_duplicate_node_id(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.create_nodes_csv(
                directory,
                [
                    {
                        "id": "1",
                        "latitude": "13.0",
                        "longitude": "80.0",
                    },
                    {
                        "id": "1",
                        "latitude": "13.1",
                        "longitude": "80.1",
                    },
                ],
            )

            with self.assertRaises(ValueError):
                load_nodes(path)

    def test_invalid_latitude(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.create_nodes_csv(
                directory,
                [
                    {
                        "id": "1",
                        "latitude": "100.0",
                        "longitude": "80.0",
                    },
                ],
            )

            with self.assertRaises(ValueError):
                load_nodes(path)

    def test_invalid_longitude(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.create_nodes_csv(
                directory,
                [
                    {
                        "id": "1",
                        "latitude": "13.0",
                        "longitude": "200.0",
                    },
                ],
            )

            with self.assertRaises(ValueError):
                load_nodes(path)

    def test_missing_required_column(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.create_nodes_csv(
                directory,
                [
                    {
                        "id": "1",
                        "latitude": "13.0",
                    },
                ],
                columns=[
                    "id",
                    "latitude",
                ],
            )

            with self.assertRaises(ValueError):
                load_nodes(path)


class TestLoadEdges(unittest.TestCase):
    """Tests for OSM edge loading."""

    def create_edges_csv(
        self,
        directory: str,
        rows: list[dict[str, str]],
        columns=None,
    ) -> Path:
        """Create a temporary edges CSV."""

        path = Path(directory) / "edges.csv"

        if columns is None:
            columns = [
                "from",
                "to",
                "distance",
                "road_type",
                "road_name",
                "oneway",
            ]

        with path.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=columns,
            )

            writer.writeheader()
            writer.writerows(rows)

        return path

    def valid_edge(
        self,
        from_node="1",
        to_node="2",
        distance="100",
        road_type="residential",
        road_name="Test Road",
        oneway="False",
    ):
        return {
            "from": from_node,
            "to": to_node,
            "distance": distance,
            "road_type": road_type,
            "road_name": road_name,
            "oneway": oneway,
        }

    def test_load_valid_edges(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.create_edges_csv(
                directory,
                [
                    self.valid_edge(),
                ],
            )

            graph, edges = load_edges(
                path,
                speed_kmh=40,
            )

            self.assertEqual(
                len(edges),
                1,
            )

            self.assertIn(
                1,
                graph,
            )

            self.assertEqual(
                edges[0].from_node,
                1,
            )

            self.assertEqual(
                edges[0].to_node,
                2,
            )

            self.assertEqual(
                edges[0].distance_m,
                100.0,
            )

            self.assertEqual(
                edges[0].road_type,
                "residential",
            )

            self.assertEqual(
                edges[0].road_name,
                "Test Road",
            )

            self.assertFalse(
                edges[0].oneway,
            )

    def test_edge_id_is_unique(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.create_edges_csv(
                directory,
                [
                    self.valid_edge(
                        distance="100",
                    ),
                    self.valid_edge(
                        distance="200",
                    ),
                    self.valid_edge(
                        distance="300",
                    ),
                ],
            )

            _, edges = load_edges(path)

            edge_ids = [
                edge.edge_id
                for edge in edges
            ]

            self.assertEqual(
                edge_ids,
                [0, 1, 2],
            )

            self.assertEqual(
                len(edge_ids),
                len(set(edge_ids)),
            )

    def test_parallel_edges_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.create_edges_csv(
                directory,
                [
                    self.valid_edge(
                        distance="100",
                        road_name="Road A",
                    ),
                    self.valid_edge(
                        distance="120",
                        road_name="Road B",
                    ),
                ],
            )

            graph, edges = load_edges(path)

            self.assertEqual(
                len(edges),
                2,
            )

            self.assertEqual(
                len(graph[1]),
                2,
            )

            self.assertNotEqual(
                edges[0].edge_id,
                edges[1].edge_id,
            )

    def test_self_loop_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.create_edges_csv(
                directory,
                [
                    self.valid_edge(
                        from_node="1",
                        to_node="1",
                        distance="50",
                    ),
                ],
            )

            graph, edges = load_edges(path)

            self.assertEqual(
                len(edges),
                1,
            )

            self.assertEqual(
                edges[0].from_node,
                1,
            )

            self.assertEqual(
                edges[0].to_node,
                1,
            )

            self.assertEqual(
                len(graph[1]),
                1,
            )

    def test_invalid_distance_zero(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.create_edges_csv(
                directory,
                [
                    self.valid_edge(
                        distance="0",
                    ),
                ],
            )

            with self.assertRaises(ValueError):
                load_edges(path)

    def test_invalid_distance_negative(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.create_edges_csv(
                directory,
                [
                    self.valid_edge(
                        distance="-10",
                    ),
                ],
            )

            with self.assertRaises(ValueError):
                load_edges(path)

    def test_invalid_oneway_value(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.create_edges_csv(
                directory,
                [
                    self.valid_edge(
                        oneway="maybe",
                    ),
                ],
            )

            with self.assertRaises(ValueError):
                load_edges(path)

    def test_invalid_speed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.create_edges_csv(
                directory,
                [
                    self.valid_edge(),
                ],
            )

            with self.assertRaises(ValueError):
                load_edges(
                    path,
                    speed_kmh=0,
                )

    def test_missing_edges_file(self):
        with self.assertRaises(FileNotFoundError):
            load_edges(
                "does_not_exist.csv"
            )

    def test_missing_required_column(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.create_edges_csv(
                directory,
                [
                    {
                        "from": "1",
                        "to": "2",
                        "distance": "100",
                    },
                ],
                columns=[
                    "from",
                    "to",
                    "distance",
                ],
            )

            with self.assertRaises(ValueError):
                load_edges(path)

    def test_oneway_flag_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.create_edges_csv(
                directory,
                [
                    self.valid_edge(
                        oneway="True",
                    ),
                ],
            )

            _, edges = load_edges(path)

            self.assertTrue(
                edges[0].oneway
            )

    def test_base_travel_time_is_calculated(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.create_edges_csv(
                directory,
                [
                    self.valid_edge(
                        distance="1000",
                    ),
                ],
            )

            _, edges = load_edges(
                path,
                speed_kmh=40,
            )

            self.assertAlmostEqual(
                edges[0].base_travel_time_min,
                1.5,
            )


class TestGraphValidation(unittest.TestCase):
    """Tests for graph/node consistency validation."""

    def test_missing_graph_node_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "edges.csv"

            with path.open(
                "w",
                encoding="utf-8",
                newline="",
            ) as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=[
                        "from",
                        "to",
                        "distance",
                        "road_type",
                        "road_name",
                        "oneway",
                    ],
                )

                writer.writeheader()

                writer.writerow(
                    {
                        "from": "1",
                        "to": "999",
                        "distance": "100",
                        "road_type": "residential",
                        "road_name": "Test",
                        "oneway": "False",
                    }
                )

            graph, _ = load_edges(path)

            coordinates = {
                1: (
                    13.0,
                    80.0,
                ),
            }

            with self.assertRaises(ValueError):
                validate_graph_nodes(
                    graph,
                    coordinates,
                )


class TestRealOSMIntegration(unittest.TestCase):
    """
    Integration tests using the actual Member 1 OSM dataset.
    """

    @classmethod
    def setUpClass(cls):
        cls.project_root = (
            Path(__file__).resolve().parents[2]
        )

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

    def test_real_osm_dataset_exists(self):
        self.assertTrue(
            self.nodes_path.is_file()
        )

        self.assertTrue(
            self.edges_path.is_file()
        )

    def test_real_osm_dataset_loads(self):
        graph, coordinates, edges = (
            load_osm_graph(
                self.nodes_path,
                self.edges_path,
            )
        )

        self.assertEqual(
            len(coordinates),
            5491,
        )

        self.assertEqual(
            len(graph),
            5480,
        )

        self.assertEqual(
            len(edges),
            13475,
        )

    def test_real_osm_parallel_edges_preserved(self):
        _, _, edges = load_osm_graph(
            self.nodes_path,
            self.edges_path,
        )

        parallel_edges = [
            edge
            for edge in edges
            if (
                edge.from_node
                == 243325994
                and edge.to_node
                == 2407565892
            )
        ]

        self.assertEqual(
            len(parallel_edges),
            2,
        )

        self.assertNotEqual(
            parallel_edges[0].edge_id,
            parallel_edges[1].edge_id,
        )

        self.assertAlmostEqual(
            parallel_edges[0].distance_m,
            96.29762641677289,
        )

        self.assertAlmostEqual(
            parallel_edges[1].distance_m,
            97.70344086362354,
        )

    def test_default_speed_is_positive(self):
        self.assertGreater(
            DEFAULT_SPEED_KMH,
            0,
        )


if __name__ == "__main__":
    unittest.main()