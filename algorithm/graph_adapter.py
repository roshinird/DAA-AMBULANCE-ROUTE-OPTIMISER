"""
Graph adapter for the Ambulance Route Optimizer.

This module converts the OSM CSV output produced by Member 1
into data structures that can be consumed by the Member 2
A* routing engine.

Input files:
    data/nodes.csv
    data/edges.csv

The adapter does not modify the source CSV files.
"""

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


DEFAULT_SPEED_KMH = 40.0


@dataclass(frozen=True)
class Edge:
    """
    Represents one directed road segment.

    Each OSM edge receives its own identity so that duplicate
    from -> to pairs are not accidentally merged.
    """

    edge_id: int
    from_node: int
    to_node: int
    distance_m: float
    road_type: str
    road_name: str
    oneway: bool
    base_travel_time_min: float


def _validate_speed(speed_kmh: float) -> None:
    """Validate a road speed value."""

    if not isinstance(speed_kmh, (int, float)):
        raise TypeError("speed_kmh must be a number.")

    if not math.isfinite(speed_kmh) or speed_kmh <= 0:
        raise ValueError(
            "speed_kmh must be a finite value greater than zero."
        )


def _parse_bool(value: str) -> bool:
    """
    Convert a CSV boolean value into Python bool.

    Accepted true values:
        true, 1, yes

    Accepted false values:
        false, 0, no

    The comparison is case-insensitive.
    """

    normalized = str(value).strip().lower()

    if normalized in {"true", "1", "yes"}:
        return True

    if normalized in {"false", "0", "no"}:
        return False

    raise ValueError(f"Invalid boolean value: {value}")


def _parse_required_float(value: str, field_name: str) -> float:
    """Parse and validate a required floating-point value."""

    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Invalid {field_name}: {value}"
        ) from exc

    if not math.isfinite(number):
        raise ValueError(
            f"{field_name} must be finite."
        )

    return number


def _parse_required_int(value: str, field_name: str) -> int:
    """Parse and validate a required integer value."""

    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Invalid {field_name}: {value}"
        ) from exc


def distance_to_travel_time(
    distance_m: float,
    speed_kmh: float,
) -> float:
    """
    Convert road distance in meters into travel time in minutes.

    Formula:

        time_hours = distance_km / speed_kmh
        time_minutes = time_hours * 60
    """

    if not isinstance(distance_m, (int, float)):
        raise TypeError("distance_m must be a number.")

    if not math.isfinite(distance_m) or distance_m <= 0:
        raise ValueError(
            "distance_m must be a finite value greater than zero."
        )

    _validate_speed(speed_kmh)

    distance_km = distance_m / 1000.0
    travel_time_hours = distance_km / speed_kmh

    return travel_time_hours * 60.0


def load_nodes(nodes_path: str | Path) -> Dict[int, Tuple[float, float]]:
    """
    Load OSM node coordinates.

    Returns:

        {
            node_id: (latitude, longitude),
            ...
        }
    """

    path = Path(nodes_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Nodes file not found: {path}"
        )

    coordinates: Dict[int, Tuple[float, float]] = {}

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        required_columns = {
            "id",
            "latitude",
            "longitude",
        }

        actual_columns = set(reader.fieldnames or [])

        missing_columns = required_columns - actual_columns

        if missing_columns:
            raise ValueError(
                "nodes.csv is missing required columns: "
                + ", ".join(sorted(missing_columns))
            )

        for row_number, row in enumerate(reader, start=2):

            node_id = _parse_required_int(
                row["id"],
                f"node id on row {row_number}",
            )

            latitude = _parse_required_float(
                row["latitude"],
                f"latitude on row {row_number}",
            )

            longitude = _parse_required_float(
                row["longitude"],
                f"longitude on row {row_number}",
            )

            if not -90 <= latitude <= 90:
                raise ValueError(
                    f"Latitude for node {node_id} must be "
                    f"between -90 and 90."
                )

            if not -180 <= longitude <= 180:
                raise ValueError(
                    f"Longitude for node {node_id} must be "
                    f"between -180 and 180."
                )

            if node_id in coordinates:
                raise ValueError(
                    f"Duplicate node id found: {node_id}"
                )

            coordinates[node_id] = (
                latitude,
                longitude,
            )

    if not coordinates:
        raise ValueError(
            "nodes.csv contains no nodes."
        )

    return coordinates


def load_edges(
    edges_path: str | Path,
    speed_kmh: float = DEFAULT_SPEED_KMH,
) -> Tuple[Dict[int, List[Edge]], List[Edge]]:
    """
    Load OSM road edges.

    Returns two structures:

        graph:
            Dictionary mapping each source node to its outgoing edges.

        edges:
            Complete list of all edges.

    Duplicate from -> to pairs are preserved.
    """

    path = Path(edges_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Edges file not found: {path}"
        )

    _validate_speed(speed_kmh)

    graph: Dict[int, List[Edge]] = {}
    all_edges: List[Edge] = []

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        required_columns = {
            "from",
            "to",
            "distance",
            "road_type",
            "road_name",
            "oneway",
        }

        actual_columns = set(reader.fieldnames or [])

        missing_columns = required_columns - actual_columns

        if missing_columns:
            raise ValueError(
                "edges.csv is missing required columns: "
                + ", ".join(sorted(missing_columns))
            )

        for row_number, row in enumerate(reader, start=2):

            from_node = _parse_required_int(
                row["from"],
                f"from node on row {row_number}",
            )

            to_node = _parse_required_int(
                row["to"],
                f"to node on row {row_number}",
            )

            distance_m = _parse_required_float(
                row["distance"],
                f"distance on row {row_number}",
            )

            if distance_m <= 0:
                raise ValueError(
                    f"Distance on row {row_number} "
                    f"must be greater than zero."
                )

            oneway = _parse_bool(
                row["oneway"]
            )

            road_type = (
                row["road_type"] or ""
            ).strip()

            road_name = (
                row["road_name"] or ""
            ).strip()

            base_travel_time_min = distance_to_travel_time(
                distance_m,
                speed_kmh,
            )

            edge = Edge(
                edge_id=len(all_edges),
                from_node=from_node,
                to_node=to_node,
                distance_m=distance_m,
                road_type=road_type,
                road_name=road_name,
                oneway=oneway,
                base_travel_time_min=base_travel_time_min,
            )

            all_edges.append(edge)

            if from_node not in graph:
                graph[from_node] = []

            graph[from_node].append(edge)

    if not all_edges:
        raise ValueError(
            "edges.csv contains no edges."
        )

    return graph, all_edges


def load_osm_graph(
    nodes_path: str | Path,
    edges_path: str | Path,
    speed_kmh: float = DEFAULT_SPEED_KMH,
):
    """
    Load the complete OSM routing data.

    Returns:

        graph:
            Outgoing edges indexed by source node.

        coordinates:
            Node coordinates.

        edges:
            Complete list of OSM edges.
    """

    coordinates = load_nodes(nodes_path)

    graph, edges = load_edges(
        edges_path,
        speed_kmh=speed_kmh,
    )

    missing_from_nodes = set()

    for edge in edges:
        if edge.from_node not in coordinates:
            missing_from_nodes.add(edge.from_node)

        if edge.to_node not in coordinates:
            missing_from_nodes.add(edge.to_node)

    if missing_from_nodes:
        sample = sorted(missing_from_nodes)[:10]

        raise ValueError(
            "edges.csv references nodes that are missing "
            f"from nodes.csv. Sample: {sample}"
        )

    return graph, coordinates, edges