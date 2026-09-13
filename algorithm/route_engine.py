"""
High-level route engine for the Ambulance Route Optimizer.

Member 2 responsibility:
    Provide a clean interface for the rest of the application
    to request an ambulance route.

The route engine:
    1. Loads the OSM road graph.
    2. Keeps the graph and node coordinates available.
    3. Passes start/goal nodes and current traffic weights to A*.
    4. Converts the A* result into a backend-friendly dictionary.

This module does not modify:
    - Member 1's OSM pipeline
    - The original CSV files
    - The graph structure during routing
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from algorithm.astar import (
    MAX_AMBULANCE_SPEED_KMH,
    RouteResult,
    astar,
)
from algorithm.graph_adapter import (
    Edge,
    load_osm_graph,
)


class RouteEngine:
    """
    High-level interface for ambulance routing.

    The graph is loaded once when the engine is created.
    Individual route requests can then use different traffic
    multipliers without rebuilding the OSM graph.
    """

    def __init__(
        self,
        nodes_path: str,
        edges_path: str,
        speed_kmh: float = 40.0,
        max_ambulance_speed_kmh: float = (
            MAX_AMBULANCE_SPEED_KMH
        ),
    ) -> None:

        (
            self.graph,
            self.coordinates,
            self.edges,
        ) = load_osm_graph(
            nodes_path,
            edges_path,
            speed_kmh=speed_kmh,
        )

        self.max_ambulance_speed_kmh = (
            max_ambulance_speed_kmh
        )

    def find_route(
        self,
        start_node: int,
        goal_node: int,
        traffic_multipliers: Optional[
            Dict[int, float]
        ] = None,
    ) -> Optional[Dict[str, object]]:
        """
        Find the best ambulance route.

        Parameters
        ----------
        start_node:
            OSM node ID where the ambulance starts.

        goal_node:
            OSM node ID representing the destination.

        traffic_multipliers:
            Optional mapping:

                edge_id -> traffic multiplier

            Missing edges use multiplier 1.0.

        Returns
        -------
        dict | None

        Successful result:

            {
                "route": [...],
                "distance_km": 3.05,
                "travel_time_min": 4.58
            }

        Returns None when no route exists.
        """

        result = astar(
            graph=self.graph,
            coordinates=self.coordinates,
            start=start_node,
            goal=goal_node,
            traffic_multipliers=traffic_multipliers,
            max_ambulance_speed_kmh=(
                self.max_ambulance_speed_kmh
            ),
        )

        if result is None:
            return None

        return self._format_result(result)

    def find_route_result(
        self,
        start_node: int,
        goal_node: int,
        traffic_multipliers: Optional[
            Dict[int, float]
        ] = None,
    ) -> Optional[RouteResult]:
        """
        Return the raw RouteResult from the A* engine.

        This is useful internally when another component needs
        access to the selected Edge objects.
        """

        return astar(
            graph=self.graph,
            coordinates=self.coordinates,
            start=start_node,
            goal=goal_node,
            traffic_multipliers=traffic_multipliers,
            max_ambulance_speed_kmh=(
                self.max_ambulance_speed_kmh
            ),
        )

    def _format_result(
        self,
        result: RouteResult,
    ) -> Dict[str, object]:
        """
        Convert the immutable A* result into a simple
        backend-friendly dictionary.
        """

        return {
            "route": list(result.route),
            "distance_km": result.distance_km,
            "travel_time_min": result.travel_time_min,
        }

    def get_node_coordinates(
        self,
        node_id: int,
    ) -> Tuple[float, float]:
        """
        Return the latitude/longitude of an OSM node.
        """

        if node_id not in self.coordinates:
            raise KeyError(
                f"Node {node_id} is missing from the OSM graph."
            )

        return self.coordinates[node_id]

    def get_edge_count(self) -> int:
        """
        Return the number of directed OSM edges loaded.
        """

        return len(self.edges)

    def get_node_count(self) -> int:
        """
        Return the number of OSM nodes loaded.
        """

        return len(self.coordinates)