import json
import math
import heapq


NODES_FILE = "data/processed/nodes.json"
EDGES_FILE = "data/processed/edges.json"

MAX_SPEED_KPH = 60.0


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

    The straight-line distance is divided by the maximum graph speed.
    This keeps the heuristic in seconds, matching the travel-time cost
    used by A*.
    """

    lat1, lon1 = nodes[node_a]
    lat2, lon2 = nodes[node_b]

    radius = 6371000  # Earth radius in metres

    # Maximum speed in the graph: 60 km/h converted to m/s.
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


def a_star(graph, nodes, start, goal):
    """
    Find the shortest-travel-time path from start to goal using A*.

    Returns:
        path: list of node IDs
        total_time: total travel time in seconds
    """

    open_set = []

    start_heuristic = heuristic(start, goal, nodes)

    heapq.heappush(
        open_set,
        (start_heuristic, start)
    )

    came_from = {}

    g_score = {
        start: 0
    }

    while open_set:

        _, current = heapq.heappop(open_set)

        if current == goal:
            path = reconstruct_path(came_from, current)
            return path, g_score[current]

        for edge in graph.get(current, []):

            neighbor = edge["target"]

            tentative_g_score = (
                g_score[current]
                + edge["travel_time_s"]
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


if __name__ == "__main__":

    nodes, graph = load_graph()

    print(f"Loaded {len(nodes)} nodes.")
    print(
        f"Loaded {sum(len(edges) for edges in graph.values())} directed edges."
    )