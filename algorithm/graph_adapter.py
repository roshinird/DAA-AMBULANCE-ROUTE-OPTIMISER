"""
Graph adapter for the Ambulance Route Optimizer.

Member 2 responsibility:
    Convert the real OSM CSV data produced by Member 1 into a
    validated routing graph suitable for the A* route engine.

Input:
    data/nodes.csv
    data/edges.csv

Design goals:
    - Preserve every OSM edge.
    - Preserve parallel edges.
    - Preserve self-loop edges.
    - Preserve directed edge orientation.
    - Preserve OSM road metadata.
    - Calculate base travel time.
    - Validate all important input values.
    - Never modify Member 1's source files.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


DEFAULT_SPEED_KMH = 40.0


@dataclass(frozen=True)
class Edge:
    """
    Represents one directed OSM road segment.
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
    """Validate the configured routing speed."""

    if not isinstance(speed_kmh, (int, float)):
        raise TypeError("speed_kmh must be a number.")

    if not math.isfinite(speed_kmh):
        raise ValueError("speed_kmh must be finite.")

    if speed_kmh <= 0:
        raise ValueError(
            "speed_kmh must be greater than zero."
        )


def _parse_bool(value: str) -> bool:
    """
    Convert a CSV boolean value into Python bool.

    Accepted true values:
        true
        1
        yes

    Accepted false values:
        false
        0
        no
    """

    normalized = str(value).strip().lower()

    if normalized in {"true", "1", "yes"}:
        return True

    if normalized in {"false", "0", "no"}:
        return False

    raise ValueError(
        f"Invalid boolean value: {value}"
    )


def _parse_required_int(
    value: str,
    field_name: str,
) -> int:
    """Parse a required integer CSV field."""

    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Invalid {field_name}: {value}"
        ) from exc


def _parse_required_float(
    value: str,
    field_name: str,
) -> float:
    """Parse and validate a required floating-point field."""

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


def distance_to_travel_time(
    distance_m: float,
    speed_kmh: float,
) -> float:
    """
    Convert distance in meters into travel time in minutes.

    Formula:

        distance_km = distance_m / 1000
        time_hours = distance_km / speed_kmh
        time_minutes = time_hours * 60
    """

    if not isinstance(distance_m, (int, float)):
        raise TypeError(
            "distance_m must be a number."
        )

    if not math.isfinite(distance_m):
        raise ValueError(
            "distance_m must be finite."
        )

    if distance_m <= 0:
        raise ValueError(
            "distance_m must be greater than zero."
        )

    _validate_speed(speed_kmh)

    distance_km = distance_m / 1000.0

    travel_time_hours = (
        distance_km / speed_kmh
    )

    return travel_time_hours * 60.0


def _validate_coordinates(
    latitude: float,
    longitude: float,
    node_id: int,
) -> None:
    """Validate a geographic coordinate."""

    if not -90.0 <= latitude <= 90.0:
        raise ValueError(
            f"Latitude for node {node_id} must be "
            "between -90 and 90."
        )

    if not -180.0 <= longitude <= 180.0:
        raise ValueError(
            f"Longitude for node {node_id} must be "
            "between -180 and 180."
        )


def _validate_csv_columns(
    actual_columns,
    required_columns,
    filename: str,
) -> None:
    """Ensure all required CSV columns are present."""

    missing_columns = (
        set(required_columns) - set(actual_columns)
    )

    if missing_columns:
        raise ValueError(
            f"{filename} is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )


def load_nodes(
    nodes_path: str | Path,
) -> Dict[int, Tuple[float, float]]:
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

    coordinates: Dict[
        int,
        Tuple[float, float],
    ] = {}

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        _validate_csv_columns(
            reader.fieldnames or [],
            {
                "id",
                "latitude",
                "longitude",
            },
            path.name,
        )

        for row_number, row in enumerate(
            reader,
            start=2,
        ):
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

            _validate_coordinates(
                latitude,
                longitude,
                node_id,
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
) -> Tuple[
    Dict[int, List[Edge]],
    List[Edge],
]:
    """
    Load OSM road edges.

    Returns:

        graph:
            Directed outgoing edges indexed by source node.

        edges:
            Complete ordered list of OSM edges.

    Parallel edges and self-loops are intentionally preserved.
    """

    path = Path(edges_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Edges file not found: {path}"
        )

    _validate_speed(speed_kmh)

    graph: Dict[
        int,
        List[Edge],
    ] = {}

    all_edges: List[Edge] = []

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        _validate_csv_columns(
            reader.fieldnames or [],
            {
                "from",
                "to",
                "distance",
                "road_type",
                "road_name",
                "oneway",
            },
            path.name,
        )

        for row_number, row in enumerate(
            reader,
            start=2,
        ):
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
                    "must be greater than zero."
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

            base_travel_time_min = (
                distance_to_travel_time(
                    distance_m,
                    speed_kmh,
                )
            )

            edge = Edge(
                edge_id=len(all_edges),
                from_node=from_node,
                to_node=to_node,
                distance_m=distance_m,
                road_type=road_type,
                road_name=road_name,
                oneway=oneway,
                base_travel_time_min=(
                    base_travel_time_min
                ),
            )

            all_edges.append(edge)

            graph.setdefault(
                from_node,
                [],
            ).append(edge)

    if not all_edges:
        raise ValueError(
            "edges.csv contains no edges."
        )

    return graph, all_edges


def validate_graph_nodes(
    graph: Dict[int, List[Edge]],
    coordinates: Dict[int, Tuple[float, float]],
) -> None:
    """
    Ensure every edge references an existing OSM node.
    """

    missing_nodes = set()

    for outgoing_edges in graph.values():

        for edge in outgoing_edges:

            if edge.from_node not in coordinates:
                missing_nodes.add(
                    edge.from_node
                )

            if edge.to_node not in coordinates:
                missing_nodes.add(
                    edge.to_node
                )

    if missing_nodes:
        sample = sorted(
            missing_nodes
        )[:10]

        raise ValueError(
            "edges.csv references nodes that are "
            "missing from nodes.csv. "
            f"Sample: {sample}"
        )


def load_osm_graph(
    nodes_path: str | Path,
    edges_path: str | Path,
    speed_kmh: float = DEFAULT_SPEED_KMH,
) -> Tuple[
    Dict[int, List[Edge]],
    Dict[int, Tuple[float, float]],
    List[Edge],
]:
    """
    Load and validate the complete OSM routing dataset.

    Returns:

        graph:
            Directed adjacency structure.

        coordinates:
            OSM node coordinates.

        edges:
            Complete list of OSM edges.
    """

    coordinates = load_nodes(
        nodes_path
    )

    graph, edges = load_edges(
        edges_path,
        speed_kmh=speed_kmh,
    )

    validate_graph_nodes(
        graph,
        coordinates,
    )

    return (
        graph,
        coordinates,
        edges,
    )