import json
from collections import defaultdict, deque

NODES_FILE = "data/processed/nodes.json"
EDGES_FILE = "data/processed/edges.json"
LOCATIONS_FILE = "data/locations/locations.json"


print("Loading graph data...")

with open(NODES_FILE, "r", encoding="utf-8") as f:
    nodes = json.load(f)

with open(EDGES_FILE, "r", encoding="utf-8") as f:
    edges = json.load(f)

with open(LOCATIONS_FILE, "r", encoding="utf-8") as f:
    locations = json.load(f)


print(f"Graph nodes: {len(nodes)}")
print(f"Graph edges: {len(edges)}")


# Build directed adjacency list
graph = defaultdict(list)

for edge in edges:
    source = str(edge["source"])
    target = str(edge["target"])
    graph[source].append(target)


def is_reachable(start, goal):
    start = str(start)
    goal = str(goal)

    queue = deque([start])
    visited = {start}

    while queue:
        current = queue.popleft()

        if current == goal:
            return True

        for neighbor in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return False


print("\nChecking patient -> hospital routes...\n")

patients = ["P1", "P2", "P3"]
hospitals = ["H1", "H2"]

all_reachable = True

for patient in patients:
    for hospital in hospitals:

        start_node = locations[patient]["graph_node_id"]
        goal_node = locations[hospital]["graph_node_id"]

        reachable = is_reachable(start_node, goal_node)

        if reachable:
            print(f"{patient} -> {hospital}: REACHABLE")
        else:
            print(f"{patient} -> {hospital}: NOT REACHABLE")
            all_reachable = False


print("\nValidation result:")

if all_reachable:
    print("PASS: All 6 patient -> hospital routes are reachable.")
else:
    print("WARNING: One or more patient -> hospital routes are not reachable.")