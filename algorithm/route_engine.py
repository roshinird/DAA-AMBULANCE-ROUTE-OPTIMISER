"""
Route engine integration layer for the Ambulance Route Optimizer.

This module connects:

    OSM CSV data
        ↓
    Graph Adapter
        ↓
    Normalized A* graph
        ↓
    Traffic weights
        ↓
    A* route engine
        ↓
    Route result

This file belongs to Member 2's algorithm module.

It does not modify Member 1's OSM data or files.
It does not generate or simulate traffic.
"""

from pathlib import Path
from typing import Any, Mapping

from algorithm.astar import astar
from algorithm.graph_adapter import (
    DEFAULT_SPEED_KMH,
    load_osm_graph,
)
from algorithm.traffic import apply_traffic_weights


def build_normalized_graph(graph):
    """
    Convert graph_adapter Edge objects into the dictionary format
    expected by the A* engine.

    Parallel edges are preserved because every edge keeps
    its unique edge_id.
    """

    normalized_graph = {}

    for node, outgoing_edges in graph.items():

        normalized_graph[node] = []

        for edge in outgoing_edges:

            normalized_graph[node].append(
                {
                    "edge_id": edge.edge_id,
                    "to": edge.to_node,
                    "distance_km": edge.distance_m / 1000.0,
                    "travel_time_min": edge.base_travel_time_min,
                    "base_travel_time_min": edge.base_travel_time_min,
                    "road_type": edge.road_type,
                    "road_name": edge.road_name,
                    "oneway": edge.oneway,
                }
            )

    return normalized_graph


def calculate_route(
    nodes_path: str | Path,
    edges_path: str | Path,
    start: int,
    goal: int,
    speed_kmh: float = DEFAULT_SPEED_KMH,
    traffic_multipliers: Mapping[int, float] | None = None,
) -> dict[str, Any] | None:
    """
    Load OSM routing data and calculate the fastest route.

    Parameters:
        nodes_path:
            Path to Member 1's nodes.csv.

        edges_path:
            Path to Member 1's edges.csv.

        start:
            Starting OSM node ID.

        goal:
            Destination OSM node ID.

        speed_kmh:
            Base ambulance travel speed.

        traffic_multipliers:
            Optional mapping from edge_id to traffic multiplier.

            Example:

                {
                    10: 1.0,
                    11: 2.0,
                    12: 3.0,
                }

            Edges not listed use normal traffic (1.0).

    Returns:
        A dictionary containing:

            route
            distance_km
            travel_time_min
            edges

        Returns None when no route exists.
    """

    graph, coordinates, _edges = load_osm_graph(
        nodes_path,
        edges_path,
        speed_kmh=speed_kmh,
    )

    normalized_graph = build_normalized_graph(graph)

    weighted_graph = apply_traffic_weights(
        normalized_graph,
        traffic_multipliers,
    )

    return astar(
        weighted_graph,
        coordinates,
        start,
        goal,
    )