"""
Robust A* route-finding engine for the Ambulance Route Optimizer.

Member 2 responsibility:
    - Find the minimum-travel-time route.
    - Respect directed road connections.
    - Support parallel road segments.
    - Support dynamically changing edge travel times.
    - Preserve the exact selected edges.
    - Calculate route distance from actual road segments.
    - Safely handle dead ends and disconnected networks.

The algorithm is independent of the OSM CSV format.

Expected normalized graph format:

graph = {
    node_id: [
        {
            "edge_id": ...,
            "to": ...,
            "distance_km": ...,
            "travel_time_min": ...,
            ...
        },
        ...
    ]
}

Coordinates format:

coordinates = {
    node_id: (latitude, longitude),
    ...
}

Important:
    Edge travel_time_min is the current routing cost.

    Therefore traffic-aware routing is achieved by changing
    edge travel_time_min before calling astar().
"""

import heapq
import math


EARTH_RADIUS_KM = 6371.0

# The heuristic assumes that an ambulance can never travel faster
# than this speed. Traffic multipliers in traffic.py are >= 1.0,
# so traffic can only increase travel time.
MAX_AMBULANCE_SPEED_KMH = 120.0


def haversine_distance(coord1, coord2):
    """
    Calculate the great-circle distance between two coordinates.

    Parameters:
        coord1: (latitude, longitude)
        coord2: (latitude, longitude)

    Returns:
        Distance in kilometres.
    """

    if not isinstance(coord1, (tuple, list)) or len(coord1) != 2:
        raise ValueError(
            "coord1 must contain latitude and longitude."
        )

    if not isinstance(coord2, (tuple, list)) or len(coord2) != 2:
        raise ValueError(
            "coord2 must contain latitude and longitude."
        )

    lat1, lon1 = coord1
    lat2, lon2 = coord2

    values = (lat1, lon1, lat2, lon2)

    if not all(
        isinstance(value, (int, float))
        and math.isfinite(value)
        for value in values
    ):
        raise ValueError(
            "Coordinates must contain finite numeric values."
        )

    if not -90 <= lat1 <= 90:
        raise ValueError(
            "Latitude must be between -90 and 90."
        )

    if not -90 <= lat2 <= 90:
        raise ValueError(
            "Latitude must be between -90 and 90."
        )

    if not -180 <= lon1 <= 180:
        raise ValueError(
            "Longitude must be between -180 and 180."
        )

    if not -180 <= lon2 <= 180:
        raise ValueError(
            "Longitude must be between -180 and 180."
        )

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)

    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    # Protect against tiny floating-point errors.
    a = min(1.0, max(0.0, a))

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a),
    )

    return EARTH_RADIUS_KM * c


def validate_coordinates(coordinates):
    """
    Validate the coordinate dictionary.

    Coordinates are required to be:

        node_id -> (latitude, longitude)

    Returns:
        None

    Raises:
        TypeError / ValueError for invalid coordinates.
    """

    if not isinstance(coordinates, dict):
        raise TypeError(
            "coordinates must be a dictionary."
        )

    for node, coordinate in coordinates.items():

        if not isinstance(coordinate, (tuple, list)):
            raise ValueError(
                f"Invalid coordinates for node {node}."
            )

        if len(coordinate) != 2:
            raise ValueError(
                f"Coordinates for node {node} "
                "must contain latitude and longitude."
            )

        latitude, longitude = coordinate

        if not isinstance(latitude, (int, float)):
            raise ValueError(
                f"Invalid latitude for node {node}."
            )

        if not isinstance(longitude, (int, float)):
            raise ValueError(
                f"Invalid longitude for node {node}."
            )

        if not math.isfinite(latitude):
            raise ValueError(
                f"Latitude for node {node} is not finite."
            )

        if not math.isfinite(longitude):
            raise ValueError(
                f"Longitude for node {node} is not finite."
            )

        if not -90 <= latitude <= 90:
            raise ValueError(
                f"Latitude for node {node} must be between -90 and 90."
            )

        if not -180 <= longitude <= 180:
            raise ValueError(
                f"Longitude for node {node} must be between -180 and 180."
            )


def _edge_destination(edge):
    """
    Extract the destination node from a normalized edge.

    Supported formats:

        Dictionary:
            {
                "to": destination,
                ...
            }

        Lightweight tuple/list:
            (destination, travel_time)
    """

    if isinstance(edge, dict):

        if "to" not in edge:
            raise ValueError(
                "Edge is missing 'to'."
            )

        return edge["to"]

    if isinstance(edge, (tuple, list)) and len(edge) >= 2:
        return edge[0]

    raise ValueError(
        "Invalid edge format."
    )


def _edge_travel_time(edge):
    """
    Extract and validate the current travel time of an edge.

    Travel time must be strictly positive.

    Zero or negative travel times are rejected because they do not
    represent a valid positive road traversal cost and can violate
    assumptions used by shortest-path algorithms.
    """

    if isinstance(edge, dict):

        if "travel_time_min" not in edge:
            raise ValueError(
                "Edge is missing 'travel_time_min'."
            )

        travel_time = edge["travel_time_min"]

    elif isinstance(edge, (tuple, list)) and len(edge) == 2:

        travel_time = edge[1]

    else:
        raise ValueError(
            "Invalid edge format."
        )

    if not isinstance(travel_time, (int, float)):
        raise ValueError(
            "Edge travel time must be numeric."
        )

    if not math.isfinite(travel_time):
        raise ValueError(
            "Edge travel time must be finite."
        )

    if travel_time <= 0:
        raise ValueError(
            "Edge travel time must be greater than zero."
        )

    return float(travel_time)


def _edge_distance(edge):
    """
    Extract and validate the actual road distance.

    Dictionary format:

        distance_km
        or
        distance

    Lightweight tuple/list format:

        (destination, travel_time, distance)

    Distance may be zero for a lightweight representation, but
    negative distances are never allowed.
    """

    if isinstance(edge, dict):

        if "distance_km" in edge:
            distance = edge["distance_km"]

        elif "distance" in edge:
            distance = edge["distance"]

        else:
            raise ValueError(
                "Edge is missing road distance."
            )

    elif isinstance(edge, (tuple, list)) and len(edge) >= 3:

        distance = edge[2]

    else:
        raise ValueError(
            "Invalid edge format."
        )

    if not isinstance(distance, (int, float)):
        raise ValueError(
            "Edge distance must be numeric."
        )

    if not math.isfinite(distance):
        raise ValueError(
            "Edge distance must be finite."
        )

    if distance < 0:
        raise ValueError(
            "Edge distance cannot be negative."
        )

    return float(distance)


def validate_graph(graph):
    """
    Validate the routing graph.

    Important design decision:

        A destination node is NOT required to appear as a key in
        the graph.

    This allows valid dead-end destinations such as:

        A -> B -> Hospital

    where Hospital has no outgoing roads.

    Parallel edges are intentionally allowed.

    The graph is not modified.
    """

    if not isinstance(graph, dict):
        raise TypeError(
            "graph must be a dictionary."
        )

    for node, edges in graph.items():

        if not isinstance(edges, (list, tuple)):
            raise ValueError(
                f"Edges from node {node} "
                "must be a list or tuple."
            )

        for edge in edges:

            destination = _edge_destination(edge)

            if destination is None:
                raise ValueError(
                    f"Edge from node {node} "
                    "has an invalid destination."
                )

            _edge_travel_time(edge)
            _edge_distance(edge)


def heuristic(node, goal, coordinates):
    """
    Calculate an admissible time-based heuristic.

    The straight-line Haversine distance is divided by the maximum
    possible ambulance speed.

    Because:

        actual road distance >= straight-line distance

    and:

        actual travel speed <= MAX_AMBULANCE_SPEED_KMH

    the heuristic cannot overestimate the minimum possible travel time
    under the current routing model.

    This preserves A* optimality when edge costs are non-negative.
    """

    if node not in coordinates:
        raise ValueError(
            f"Node {node} has no coordinates."
        )

    if goal not in coordinates:
        raise ValueError(
            f"Goal node {goal} has no coordinates."
        )

    distance_km = haversine_distance(
        coordinates[node],
        coordinates[goal],
    )

    hours = (
        distance_km
        / MAX_AMBULANCE_SPEED_KMH
    )

    return hours * 60.0


def reconstruct_path(came_from, current):
    """
    Reconstruct the node path from goal back to start.
    """

    path = [current]

    while current in came_from:

        current = came_from[current]

        path.append(current)

    path.reverse()

    return path


def _reconstruct_edge_path(came_from, current):
    """
    Reconstruct the exact edges used by the route.

    This is essential when parallel OSM edges exist between the
    same pair of nodes.
    """

    edge_path = []

    while current in came_from:

        previous, edge = came_from[current]

        edge_path.append(edge)

        current = previous

    edge_path.reverse()

    return edge_path


def calculate_route_distance(route, graph):
    """
    Calculate route distance using road-edge distances.

    Note:
        A node-only route cannot distinguish between multiple
        parallel edges with different distances.

        Therefore the A* result's exact `edges` field should be
        preferred whenever available.

    This helper remains useful for simple route representations
    and backwards compatibility.
    """

    if not isinstance(route, (list, tuple)):
        raise TypeError(
            "route must be a list or tuple."
        )

    if not isinstance(graph, dict):
        raise TypeError(
            "graph must be a dictionary."
        )

    if len(route) <= 1:
        return 0.0

    total_distance = 0.0

    for index in range(len(route) - 1):

        current = route[index]
        next_node = route[index + 1]

        matching_edge = None

        for edge in graph.get(current, []):

            if _edge_destination(edge) == next_node:

                matching_edge = edge

                break

        if matching_edge is None:
            raise ValueError(
                f"No edge found from {current} to {next_node}."
            )

        total_distance += _edge_distance(
            matching_edge
        )

    return total_distance


def _validate_route_inputs(
    graph,
    coordinates,
    start,
    goal,
):
    """
    Validate all inputs required by A*.

    Start:
        Must be present in the graph because the algorithm needs
        outgoing edges from the starting node.

    Goal:
        Must have coordinates, but does NOT need to have outgoing
        edges.

    This supports valid dead-end destination nodes.
    """

    validate_graph(graph)

    validate_coordinates(coordinates)

    if start not in graph:
        raise ValueError(
            f"Start node {start} does not exist in graph."
        )

    if start not in coordinates:
        raise ValueError(
            f"Start node {start} has no coordinates."
        )

    if goal not in coordinates:
        raise ValueError(
            f"Goal node {goal} has no coordinates."
        )


def astar(graph, coordinates, start, goal):
    """
    Find the minimum-travel-time route using A*.

    Parameters:
        graph:
            Normalized directed routing graph.

        coordinates:
            Dictionary mapping node IDs to
            (latitude, longitude).

        start:
            Starting node ID.

        goal:
            Destination node ID.

    Returns:
        Dictionary:

            {
                "route": [...],
                "distance_km": ...,
                "travel_time_min": ...,
                "edges": [...]
            }

        Returns None when no route exists.

    Guarantees:
        - Directed edges are respected.
        - Parallel edges are supported.
        - Current travel_time_min values are used.
        - Exact selected edges are returned.
        - Actual selected road distances are summed.
        - Dead-end destinations are supported.
        - Disconnected graphs return None.
        - The input graph is never modified.
    """

    _validate_route_inputs(
        graph,
        coordinates,
        start,
        goal,
    )

    if start == goal:

        return {
            "route": [start],
            "distance_km": 0.0,
            "travel_time_min": 0.0,
            "edges": [],
        }

    open_set = []

    # Counter provides deterministic priority ordering when two
    # entries have exactly the same f-score.
    counter = 0

    start_heuristic = heuristic(
        start,
        goal,
        coordinates,
    )

    heapq.heappush(
        open_set,
        (
            start_heuristic,
            counter,
            start,
            0.0,
        ),
    )

    # For each node:
    #
    #     came_from[node] = (previous_node, exact_edge)
    #
    # Keeping the exact edge is essential for parallel OSM roads.
    came_from = {}

    # g_score[node] = best known travel time from start to node.
    g_score = {
        start: 0.0,
    }

    while open_set:

        (
            _estimated_total_cost,
            _queue_counter,
            current,
            queued_g_score,
        ) = heapq.heappop(open_set)

        current_best_g = g_score.get(
            current,
            float("inf"),
        )

        # Ignore stale priority-queue entries.

        if queued_g_score > current_best_g:
            continue

        # Goal test happens when the node with the best currently
        # known cost is removed from the queue.
        #
        # With a consistent/admissible heuristic and positive edge
        # costs, this is the optimal route.
        if current == goal:

            route = reconstruct_path(
                {
                    node: previous
                    for node, (previous, _) in came_from.items()
                },
                current,
            )

            edge_path = _reconstruct_edge_path(
                came_from,
                current,
            )

            total_distance = sum(
                _edge_distance(edge)
                for edge in edge_path
            )

            total_travel_time = sum(
                _edge_travel_time(edge)
                for edge in edge_path
            )

            return {
                "route": route,
                "distance_km": total_distance,
                "travel_time_min": total_travel_time,
                "edges": edge_path,
            }

        outgoing_edges = graph.get(
            current,
            [],
        )

        for edge in outgoing_edges:

            neighbor = _edge_destination(edge)

            # A graph can contain an edge to a node that is not
            # usable by the current routing operation because its
            # coordinates are unavailable.
            #
            # Do not crash the entire route search for such an edge.
            if neighbor not in coordinates:
                continue

            edge_time = _edge_travel_time(edge)

            tentative_g_score = (
                g_score[current]
                + edge_time
            )

            previous_best = g_score.get(
                neighbor,
                float("inf"),
            )

            if tentative_g_score < previous_best:

                came_from[neighbor] = (
                    current,
                    edge,
                )

                g_score[neighbor] = (
                    tentative_g_score
                )

                estimated_total_cost = (
                    tentative_g_score
                    + heuristic(
                        neighbor,
                        goal,
                        coordinates,
                    )
                )

                counter += 1

                heapq.heappush(
                    open_set,
                    (
                        estimated_total_cost,
                        counter,
                        neighbor,
                        tentative_g_score,
                    ),
                )

    # Every reachable possibility has been exhausted.
    #
    # This is a normal routing outcome, not an algorithm failure.
    return None