import json
import math
import heapq


NODES_FILE = "data/processed/nodes.json"
EDGES_FILE = "data/processed/edges.json"

MAX_SPEED_KPH = 60.0

# Dynamic road condition settings.
# These affect only Member 2's routing logic.
TRAFFIC_MULTIPLIERS = {
    "normal": 1.0,
    "light": 1.15,
    "moderate": 1.35,
    "heavy": 1.75,
}


def load_graph():
    """Load nodes and directed edges from Member 1's OSM graph."""

    with open(NODES_FILE, "r", encoding="utf-8") as file:
        nodes_data = json.load(file)

    with open(EDGES_FILE, "r", encoding="utf-8") as file:
        edges_data = json.load(file)

    nodes = {
        node["id"]: (node["latitude"], node["longitude"])
        for node in nodes_data
    }

    graph = {}

    for edge in edges_data:
        source = edge["source"]
        target = edge["target"]

        graph.setdefault(source, []).append(
            {
                "target": target,
                "distance_m": edge["distance_m"],
                "travel_time_s": edge["base_travel_time_s"],
            }
        )

    return nodes, graph


def heuristic(node_a, node_b, nodes):
    """
    Estimate the minimum possible travel time between two nodes.

    Straight-line distance is divided by the maximum graph speed.
    The result is expressed in seconds, matching the A* travel-time cost.
    """

    lat1, lon1 = nodes[node_a]
    lat2, lon2 = nodes[node_b]

    radius = 6371000
    max_speed_mps = MAX_SPEED_KPH * 1000 / 3600

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)

    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad)
        * math.cos(lat2_rad)
        * math.sin(delta_lon / 2) ** 2
    )

    distance = 2 * radius * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return distance / max_speed_mps


def get_dynamic_travel_time(edge, traffic_conditions):
    """
    Calculate the current travel time for an edge.

    traffic_conditions maps a directed edge to a traffic condition.

    Example:
        {
            ("101", "102"): "heavy"
        }
    """

    source = edge.get("source")
    target = edge["target"]

    condition = traffic_conditions.get(
        (source, target),
        "normal"
    )

    multiplier = TRAFFIC_MULTIPLIERS.get(
        condition,
        TRAFFIC_MULTIPLIERS["normal"]
    )

    return edge["travel_time_s"] * multiplier


def a_star(
    graph,
    nodes,
    start,
    goal,
    blocked_edges=None,
    traffic_conditions=None
):
    """
    Find the shortest-travel-time route using A*.

    Parameters:
        graph:
            Directed road graph.

        nodes:
            Node coordinates.

        start:
            Starting graph node ID.

        goal:
            Destination graph node ID.

        blocked_edges:
            Set of directed edges that are currently blocked.

            Example:
                {
                    ("101", "102"),
                    ("205", "206")
                }

        traffic_conditions:
            Dictionary of traffic conditions for directed edges.

            Example:
                {
                    ("101", "102"): "heavy",
                    ("205", "206"): "moderate"
                }

    Returns:
        path:
            List of node IDs.

        total_time:
            Estimated travel time in seconds.
    """

    if blocked_edges is None:
        blocked_edges = set()

    if traffic_conditions is None:
        traffic_conditions = {}

    if start not in nodes:
        raise ValueError(f"Start node '{start}' does not exist.")

    if goal not in nodes:
        raise ValueError(f"Goal node '{goal}' does not exist.")

    open_set = []

    start_heuristic = heuristic(
        start,
        goal,
        nodes
    )

    heapq.heappush(
        open_set,
        (start_heuristic, start)
    )

    came_from = {}

    g_score = {
        start: 0.0
    }

    while open_set:

        _, current = heapq.heappop(open_set)

        if current == goal:
            path = reconstruct_path(
                came_from,
                current
            )

            return path, g_score[current]

        for edge in graph.get(current, []):

            neighbor = edge["target"]

            edge_key = (
                current,
                neighbor
            )

            # Skip roads that are currently blocked.
            if edge_key in blocked_edges:
                continue

            # Calculate the current travel time.
            current_edge = dict(edge)
            current_edge["source"] = current

            travel_time = get_dynamic_travel_time(
                current_edge,
                traffic_conditions
            )

            tentative_g_score = (
                g_score[current]
                + travel_time
            )

            if tentative_g_score < g_score.get(
                neighbor,
                float("inf")
            ):

                came_from[neighbor] = current

                g_score[neighbor] = tentative_g_score

                f_score = (
                    tentative_g_score
                    + heuristic(
                        neighbor,
                        goal,
                        nodes
                    )
                )

                heapq.heappush(
                    open_set,
                    (f_score, neighbor)
                )

    return None, float("inf")


def reconstruct_path(came_from, current):
    """Reconstruct the route from goal back to start."""

    path = [current]

    while current in came_from:
        current = came_from[current]
        path.append(current)

    path.reverse()

    return path


def route_is_valid(graph, path, blocked_edges=None):
    """
    Check whether every step in a route exists and is not blocked.
    """

    if not path:
        return False

    if blocked_edges is None:
        blocked_edges = set()

    for source, target in zip(path, path[1:]):

        if (
            source,
            target
        ) in blocked_edges:
            return False

        neighbours = graph.get(source, [])

        if not any(
            edge["target"] == target
            for edge in neighbours
        ):
            return False

    return True


if __name__ == "__main__":

    nodes, graph = load_graph()

    print(f"Loaded {len(nodes)} nodes.")
    print(
        f"Loaded "
        f"{sum(len(edges) for edges in graph.values())} "
        f"directed edges."
    )

    print("Dynamic routing support enabled.")
    print("Traffic levels: normal, light, moderate, heavy.")
    print("Road closure support: enabled.")