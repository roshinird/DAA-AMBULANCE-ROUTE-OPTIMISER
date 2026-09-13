"""
Traffic-weight integration for the Ambulance Route Optimizer.

This module belongs to Member 2.

It does NOT simulate or generate traffic.

Its responsibility is to apply traffic multipliers supplied by
another module to the travel time of routing edges before A*
is executed.
"""

import math
from typing import Mapping


DEFAULT_TRAFFIC_MULTIPLIER = 1.0

TRAFFIC_MULTIPLIERS = {
    "normal": 1.0,
    "moderate": 1.5,
    "heavy": 2.0,
    "severe": 3.0,
}


def validate_traffic_multiplier(multiplier: float) -> None:
    """
    Validate a traffic multiplier.

    A multiplier must be a finite positive number and cannot
    be less than 1.0.
    """

    if not isinstance(multiplier, (int, float)):
        raise TypeError(
            "Traffic multiplier must be a number."
        )

    if not math.isfinite(multiplier):
        raise ValueError(
            "Traffic multiplier must be finite."
        )

    if multiplier < 1.0:
        raise ValueError(
            "Traffic multiplier must be at least 1.0."
        )


def get_traffic_multiplier(level: str) -> float:
    """
    Convert a traffic level into its multiplier.

    Supported levels:

        normal   -> 1.0
        moderate -> 1.5
        heavy    -> 2.0
        severe   -> 3.0
    """

    if not isinstance(level, str):
        raise TypeError(
            "Traffic level must be a string."
        )

    normalized_level = level.strip().lower()

    if normalized_level not in TRAFFIC_MULTIPLIERS:
        raise ValueError(
            f"Unknown traffic level: {level}. "
            f"Supported levels: "
            f"{', '.join(TRAFFIC_MULTIPLIERS)}"
        )

    return TRAFFIC_MULTIPLIERS[normalized_level]


def apply_traffic_weights(
    graph: dict,
    traffic_multipliers: Mapping[int, float] | None = None,
) -> dict:
    """
    Apply traffic multipliers to a normalized routing graph.

    Parameters:
        graph:
            Normalized routing graph.

        traffic_multipliers:
            Mapping of edge_id to traffic multiplier.

            Example:

                {
                    10: 1.0,
                    11: 2.0,
                    12: 3.0,
                }

            Edges not included in the mapping use 1.0.

    Returns:
        A new graph with updated travel_time_min values.

    The original graph is never modified.
    """

    if not isinstance(graph, dict):
        raise TypeError(
            "graph must be a dictionary."
        )

    if traffic_multipliers is None:
        traffic_multipliers = {}

    if not isinstance(traffic_multipliers, Mapping):
        raise TypeError(
            "traffic_multipliers must be a mapping."
        )

    for edge_id, multiplier in traffic_multipliers.items():

        if not isinstance(edge_id, int):
            raise TypeError(
                "Traffic multiplier edge IDs must be integers."
            )

        validate_traffic_multiplier(
            multiplier
        )

    adjusted_graph = {}

    for node, outgoing_edges in graph.items():

        adjusted_graph[node] = []

        for edge in outgoing_edges:

            if not isinstance(edge, dict):
                raise TypeError(
                    "Routing graph edges must be dictionaries."
                )

            if "edge_id" not in edge:
                raise ValueError(
                    "Routing edge is missing edge_id."
                )

            if "travel_time_min" not in edge:
                raise ValueError(
                    "Routing edge is missing travel_time_min."
                )

            # Always use the original base travel time when available.
            # This prevents traffic multipliers from compounding.
            base_travel_time = edge.get(
                "base_travel_time_min",
                edge["travel_time_min"],
            )

            if not isinstance(
                base_travel_time,
                (int, float),
            ):
                raise ValueError(
                    "Base travel time must be numeric."
                )

            if not math.isfinite(
                base_travel_time
            ):
                raise ValueError(
                    "Base travel time must be finite."
                )

            if base_travel_time <= 0:
                raise ValueError(
                    "Base travel time must be greater than zero."
                )

            edge_id = edge["edge_id"]

            multiplier = traffic_multipliers.get(
                edge_id,
                DEFAULT_TRAFFIC_MULTIPLIER,
            )

            validate_traffic_multiplier(
                multiplier
            )

            adjusted_edge = dict(edge)

            adjusted_edge[
                "base_travel_time_min"
            ] = float(base_travel_time)

            adjusted_edge[
                "traffic_multiplier"
            ] = float(multiplier)

            adjusted_edge[
                "travel_time_min"
            ] = (
                float(base_travel_time)
                * float(multiplier)
            )

            adjusted_graph[node].append(
                adjusted_edge
            )

    return adjusted_graph