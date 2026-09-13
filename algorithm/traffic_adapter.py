"""
Traffic data adapter for the Member-2 A* routing engine.

This module does NOT simulate traffic.

Its responsibility is to validate and normalize traffic information
provided by an external traffic simulator, such as Member 3's module.

Traffic is represented as:

    edge_id -> traffic multiplier

Examples:

    0 -> 1.0   normal traffic
    1 -> 1.5   moderate traffic
    2 -> 2.0   heavy traffic
    3 -> 3.0   severe traffic
"""

from __future__ import annotations

import math
from typing import Mapping


def validate_traffic_multiplier(value: float) -> float:
    """
    Validate and return a traffic multiplier.

    A multiplier must be:
    - numeric
    - finite
    - greater than zero

    Examples:
        1.0 -> normal traffic
        1.5 -> 50% higher travel time
        2.0 -> twice the base travel time

    Values below 1.0 are allowed because the adapter does not decide
    how traffic conditions are generated. It only validates the value.
    """

    if isinstance(value, bool):
        raise ValueError("Traffic multiplier must be a number.")

    try:
        multiplier = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Traffic multiplier must be a number."
        ) from exc

    if not math.isfinite(multiplier):
        raise ValueError(
            "Traffic multiplier must be finite."
        )

    if multiplier <= 0:
        raise ValueError(
            "Traffic multiplier must be greater than zero."
        )

    return multiplier


def validate_edge_id(edge_id: int) -> int:
    """
    Validate an edge ID.

    Edge IDs are integer identifiers assigned by the graph adapter.
    """

    if isinstance(edge_id, bool):
        raise ValueError("Edge ID must be an integer.")

    if not isinstance(edge_id, int):
        raise ValueError("Edge ID must be an integer.")

    if edge_id < 0:
        raise ValueError("Edge ID must not be negative.")

    return edge_id


def normalize_traffic_multipliers(
    traffic_multipliers: Mapping[int, float] | None,
) -> dict[int, float]:
    """
    Validate and normalize traffic multipliers.

    Parameters
    ----------
    traffic_multipliers:
        Mapping of:

            edge_id -> traffic multiplier

        Example:

            {
                0: 1.0,
                1: 1.5,
                2: 2.0,
            }

        None means no traffic overrides were supplied.

    Returns
    -------
    dict[int, float]
        A new validated dictionary.

    Notes
    -----
    The input mapping is never modified.
    """

    if traffic_multipliers is None:
        return {}

    if not isinstance(traffic_multipliers, Mapping):
        raise ValueError(
            "Traffic multipliers must be a mapping of edge IDs to multipliers."
        )

    normalized: dict[int, float] = {}

    for edge_id, multiplier in traffic_multipliers.items():
        valid_edge_id = validate_edge_id(edge_id)
        valid_multiplier = validate_traffic_multiplier(multiplier)

        normalized[valid_edge_id] = valid_multiplier

    return normalized


def get_traffic_multiplier(
    edge_id: int,
    traffic_multipliers: Mapping[int, float] | None,
    default: float = 1.0,
) -> float:
    """
    Get the traffic multiplier for one edge.

    If the edge does not have a traffic override, the default multiplier
    is returned.

    Example:

        traffic = {
            10: 1.0,
            11: 2.0,
        }

        get_traffic_multiplier(11, traffic)
        -> 2.0

        get_traffic_multiplier(50, traffic)
        -> 1.0
    """

    valid_edge_id = validate_edge_id(edge_id)
    valid_default = validate_traffic_multiplier(default)

    if traffic_multipliers is None:
        return valid_default

    normalized = normalize_traffic_multipliers(traffic_multipliers)

    return normalized.get(valid_edge_id, valid_default)