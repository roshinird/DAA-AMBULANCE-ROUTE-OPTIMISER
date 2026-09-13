"""
A* route engine for the Ambulance Route Optimizer.

Member 2 responsibility:
    Find the minimum-travel-time route between two nodes in the
    directed OSM routing graph.

Algorithm:
    A* search using

        f(n) = g(n) + h(n)

    where:
        g(n) = accumulated travel time from the start node
        h(n) = estimated remaining travel time

The heuristic uses geographic distance between nodes and the
maximum ambulance speed. This keeps the heuristic admissible
when edge travel times are based on speeds that do not exceed
the configured maximum ambulance speed.

Important properties:
    - Supports directed graphs.
    - Supports parallel edges.
    - Preserves the exact selected Edge objects.
    - Supports dynamic traffic multipliers.
    - Does not mutate the input graph.
    - Handles unreachable destinations.
    - Handles start == goal.
"""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from algorithm.graph_adapter import Edge


EARTH_RADIUS_KM = 6371.008
MAX_AMBULANCE_SPEED_KMH = 120.0


@dataclass(frozen=True)
class RouteResult:
    """
    Result returned by the A* route engine.
    """

    route: List[int]
    edges: List[Edge]
    distance_km: float
    travel_time_min: float


def haversine_distance_km(
    first: Tuple[float, float],
    second: Tuple[float, float],
) -> float:
    """
    Calculate the great-circle distance between two coordinates.

    Coordinates are supplied as:

        (latitude, longitude)

    Returns:
        Distance in kilometers.
    """

    latitude1, longitude1 = first
    latitude2, longitude2 = second

    for value, name in (
        (latitude1, "latitude1"),
        (longitude1, "longitude1"),
        (latitude2, "latitude2"),
        (longitude2, "longitude2"),
    ):
        if not isinstance(value, (int, float)):
            raise TypeError(
                f"{name} must be a number."
            )

        if not math.isfinite(value):
            raise ValueError(
                f"{name} must be finite."
            )

    if not -90.0 <= latitude1 <= 90.0:
        raise ValueError(
            "latitude1 must be between -90 and 90."
        )

    if not -90.0 <= latitude2 <= 90.0:
        raise ValueError(
            "latitude2 must be between -90 and 90."
        )

    if not -180.0 <= longitude1 <= 180.0:
        raise ValueError(
            "longitude1 must be between -180 and 180."
        )

    if not -180.0 <= longitude2 <= 180.0:
        raise ValueError(
            "longitude2 must be between -180 and 180."
        )

    latitude1_rad = math.radians(latitude1)
    latitude2_rad = math.radians(latitude2)

    delta_latitude = math.radians(
        latitude2 - latitude1
    )

    delta_longitude = math.radians(
        longitude2 - longitude1
    )

    a = (
        math.sin(delta_latitude / 2.0) ** 2
        + math.cos(latitude1_rad)
        * math.cos(latitude2_rad)
        * math.sin(delta_longitude / 2.0) ** 2
    )

    a = min(
        1.0,
        max(0.0, a),
    )

    central_angle = 2.0 * math.asin(
        math.sqrt(a)
    )

    return EARTH_RADIUS_KM * central_angle


def heuristic_time_minutes(
    node: int,
    goal: int,
    coordinates: Dict[int, Tuple[float, float]],
    max_speed_kmh: float = MAX_AMBULANCE_SPEED_KMH,
) -> float:
    """
    Estimate the minimum remaining travel time.

    The straight-line geographic distance is divided by the
    maximum ambulance speed.

    Because a straight-line distance cannot exceed the actual
    road distance and the maximum speed is an optimistic speed,
    this provides an admissible lower-bound estimate for travel
    time when actual routing speeds do not exceed max_speed_kmh.
    """

    if node not in coordinates:
        raise KeyError(
            f"Node {node} is missing from coordinates."
        )

    if goal not in coordinates:
        raise KeyError(
            f"Node {goal} is missing from coordinates."
        )

    if not isinstance(max_speed_kmh, (int, float)):
        raise TypeError(
            "max_speed_kmh must be a number."
        )

    if not math.isfinite(max_speed_kmh):
        raise ValueError(
            "max_speed_kmh must be finite."
        )

    if max_speed_kmh <= 0:
        raise ValueError(
            "max_speed_kmh must be greater than zero."
        )

    distance_km = haversine_distance_km(
        coordinates[node],
        coordinates[goal],
    )

    return (
        distance_km
        / max_speed_kmh
        * 60.0
    )


def _validate_traffic_multiplier(
    multiplier: float,
) -> None:
    """
    Validate a traffic multiplier.

    A multiplier of:

        1.0 = normal traffic
        1.5 = 50% slower
        2.0 = 100% slower

    Values below 1.0 are allowed because the engine can also
    represent unusually free-flowing conditions.
    """

    if not isinstance(
        multiplier,
        (int, float),
    ):
        raise TypeError(
            "Traffic multiplier must be a number."
        )

    if not math.isfinite(multiplier):
        raise ValueError(
            "Traffic multiplier must be finite."
        )

    if multiplier <= 0:
        raise ValueError(
            "Traffic multiplier must be greater than zero."
        )


def _edge_travel_time(
    edge: Edge,
    traffic_multiplier: float,
) -> float:
    """
    Calculate the effective travel time for an edge.
    """

    _validate_traffic_multiplier(
        traffic_multiplier
    )

    base_time = edge.base_travel_time_min

    if not isinstance(
        base_time,
        (int, float),
    ):
        raise TypeError(
            "Edge travel time must be numeric."
        )

    if not math.isfinite(base_time):
        raise ValueError(
            "Edge travel time must be finite."
        )

    if base_time < 0:
        raise ValueError(
            "Edge travel time cannot be negative."
        )

    return (
        base_time
        * traffic_multiplier
    )


def _reconstruct_route(
    start: int,
    goal: int,
    came_from: Dict[int, Tuple[int, Edge]],
) -> Tuple[List[int], List[Edge]]:
    """
    Reconstruct the node and edge path after A* reaches the goal.
    """

    route_nodes = [goal]
    route_edges: List[Edge] = []

    current = goal

    while current != start:

        if current not in came_from:
            raise RuntimeError(
                "Route reconstruction failed."
            )

        previous, edge = came_from[current]

        route_edges.append(edge)
        route_nodes.append(previous)

        current = previous

    route_nodes.reverse()
    route_edges.reverse()

    return route_nodes, route_edges


def astar(
    graph: Dict[int, List[Edge]],
    coordinates: Dict[int, Tuple[float, float]],
    start: int,
    goal: int,
    traffic_multipliers: Optional[
        Dict[int, float]
    ] = None,
    max_ambulance_speed_kmh: float = (
        MAX_AMBULANCE_SPEED_KMH
    ),
) -> Optional[RouteResult]:
    """
    Find the minimum-travel-time route using A*.

    Parameters
    ----------
    graph:
        Directed adjacency structure returned by
        graph_adapter.load_edges().

    coordinates:
        Node coordinates returned by
        graph_adapter.load_nodes().

    start:
        Starting OSM node ID.

    goal:
        Destination OSM node ID.

    traffic_multipliers:
        Optional mapping:

            edge_id -> traffic multiplier

        If an edge is not present in this mapping, multiplier 1.0
        is used.

    max_ambulance_speed_kmh:
        Maximum speed used by the heuristic.

    Returns
    -------
    RouteResult | None
        The optimal route, or None when the goal is unreachable.
    """

    if not isinstance(start, int):
        raise TypeError(
            "start must be an integer node ID."
        )

    if not isinstance(goal, int):
        raise TypeError(
            "goal must be an integer node ID."
        )

    if start not in coordinates:
        raise KeyError(
            f"Start node {start} is missing from coordinates."
        )

    if goal not in coordinates:
        raise KeyError(
            f"Goal node {goal} is missing from coordinates."
        )

    if not isinstance(
        max_ambulance_speed_kmh,
        (int, float),
    ):
        raise TypeError(
            "max_ambulance_speed_kmh must be a number."
        )

    if not math.isfinite(
        max_ambulance_speed_kmh
    ):
        raise ValueError(
            "max_ambulance_speed_kmh must be finite."
        )

    if max_ambulance_speed_kmh <= 0:
        raise ValueError(
            "max_ambulance_speed_kmh must be greater than zero."
        )

    if traffic_multipliers is None:
        traffic_multipliers = {}

    if not isinstance(
        traffic_multipliers,
        dict,
    ):
        raise TypeError(
            "traffic_multipliers must be a dictionary."
        )

    for edge_id, multiplier in (
        traffic_multipliers.items()
    ):
        if not isinstance(
            edge_id,
            int,
        ):
            raise TypeError(
                "Traffic multiplier keys must be edge IDs."
            )

        _validate_traffic_multiplier(
            multiplier
        )

    if start == goal:
        return RouteResult(
            route=[start],
            edges=[],
            distance_km=0.0,
            travel_time_min=0.0,
        )

    # Priority queue entries contain:
    #
    #   (f_score, tie_breaker, node)
    #
    # The tie breaker prevents Python from attempting to compare
    # node IDs when f_scores are equal.
    open_heap = []

    tie_breaker = 0

    start_h = heuristic_time_minutes(
        start,
        goal,
        coordinates,
        max_speed_kmh=(
            max_ambulance_speed_kmh
        ),
    )

    heapq.heappush(
        open_heap,
        (
            start_h,
            tie_breaker,
            start,
        ),
    )

    g_score: Dict[int, float] = {
        start: 0.0
    }

    came_from: Dict[
        int,
        Tuple[int, Edge],
    ] = {}

    closed_nodes = set()

    while open_heap:

        _, _, current = heapq.heappop(
            open_heap
        )

        if current in closed_nodes:
            continue

        if current == goal:
            route_nodes, route_edges = (
                _reconstruct_route(
                    start,
                    goal,
                    came_from,
                )
            )

            total_distance_m = sum(
                edge.distance_m
                for edge in route_edges
            )

            total_travel_time_min = sum(
                _edge_travel_time(
                    edge,
                    traffic_multipliers.get(
                        edge.edge_id,
                        1.0,
                    ),
                )
                for edge in route_edges
            )

            return RouteResult(
                route=route_nodes,
                edges=route_edges,
                distance_km=(
                    total_distance_m / 1000.0
                ),
                travel_time_min=(
                    total_travel_time_min
                ),
            )

        closed_nodes.add(current)

        for edge in graph.get(
            current,
            [],
        ):
            neighbor = edge.to_node

            effective_time = (
                _edge_travel_time(
                    edge,
                    traffic_multipliers.get(
                        edge.edge_id,
                        1.0,
                    ),
                )
            )

            tentative_g = (
                g_score[current]
                + effective_time
            )

            if tentative_g >= g_score.get(
                neighbor,
                math.inf,
            ):
                continue

            came_from[neighbor] = (
                current,
                edge,
            )

            g_score[neighbor] = (
                tentative_g
            )

            h_score = (
                heuristic_time_minutes(
                    neighbor,
                    goal,
                    coordinates,
                    max_speed_kmh=(
                        max_ambulance_speed_kmh
                    ),
                )
            )

            f_score = (
                tentative_g
                + h_score
            )

            tie_breaker += 1

            heapq.heappush(
                open_heap,
                (
                    f_score,
                    tie_breaker,
                    neighbor,
                ),
            )

    return None