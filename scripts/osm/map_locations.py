import json
import math

NODES_FILE = "data/processed/nodes.json"
LOCATIONS_FILE = "data/locations/locations.json"


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1)
        * math.cos(phi2)
        * math.sin(dlambda / 2) ** 2
    )

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


print("Loading graph nodes...")

with open(NODES_FILE, "r", encoding="utf-8") as f:
    nodes = json.load(f)


print("Loading locations...")

with open(LOCATIONS_FILE, "r", encoding="utf-8") as f:
    locations = json.load(f)


for location_id, location in locations.items():

    best_node = None
    best_distance = float("inf")

    for node in nodes:
        node_id = node["id"]

        distance = haversine(
            location["latitude"],
            location["longitude"],
            node["latitude"],
            node["longitude"]
        )

        if distance < best_distance:
            best_distance = distance
            best_node = node_id

    location["graph_node_id"] = best_node
    location["distance_to_graph_node_m"] = round(best_distance, 2)

    print(
        f"{location_id}: {location['name']} "
        f"-> node {best_node} "
        f"({best_distance:.2f} m)"
    )


with open(LOCATIONS_FILE, "w", encoding="utf-8") as f:
    json.dump(locations, f, indent=2)


print(f"\nUpdated: {LOCATIONS_FILE}")