import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path


RAW_FILE = Path("data/raw/koramangala.osm")
NODES_FILE = Path("data/processed/nodes.json")
EDGES_FILE = Path("data/processed/edges.json")


# Road types suitable for the ambulance road network.
ALLOWED_HIGHWAYS = {
    "motorway",
    "trunk",
    "primary",
    "secondary",
    "tertiary",
    "unclassified",
    "residential",
    "living_street",
    "service",
}

# Fallback speeds in km/h when OSM does not provide maxspeed.
DEFAULT_SPEEDS = {
    "motorway": 80,
    "trunk": 60,
    "primary": 50,
    "secondary": 40,
    "tertiary": 35,
    "unclassified": 30,
    "residential": 30,
    "living_street": 15,
    "service": 20,
}


def haversine_distance(lat1, lon1, lat2, lon2):
    """Return distance between two coordinates in metres."""
    radius = 6_371_000

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def parse_speed(value, highway):
    """Extract a numeric speed from maxspeed or use a road-type default."""
    if value:
        try:
            number = float(value.split()[0])
            return number
        except (ValueError, IndexError):
            pass

    return DEFAULT_SPEEDS.get(highway, 30)


def is_oneway(tags):
    """Return the direction rule for a road."""
    value = tags.get("oneway", "").lower()

    if value in {"yes", "true", "1"}:
        return "forward"

    if value == "-1":
        return "reverse"

    return "both"


def main():
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"OSM file not found: {RAW_FILE}")

    print("Reading OSM file...")
    root = ET.parse(RAW_FILE).getroot()

    # Read all OSM nodes.
    osm_nodes = {}

    for element in root.findall("node"):
        node_id = element.get("id")
        lat = element.get("lat")
        lon = element.get("lon")

        if node_id and lat and lon:
            osm_nodes[node_id] = {
                "id": node_id,
                "latitude": float(lat),
                "longitude": float(lon),
            }

    print(f"OSM nodes loaded: {len(osm_nodes)}")

    edges = []
    used_nodes = set()

    # Process road ways.
    for way in root.findall("way"):
        tags = {
            tag.get("k"): tag.get("v")
            for tag in way.findall("tag")
            if tag.get("k") and tag.get("v")
        }

        highway = tags.get("highway")

        if highway not in ALLOWED_HIGHWAYS:
            continue

        references = [
            node_ref.get("ref")
            for node_ref in way.findall("nd")
            if node_ref.get("ref") in osm_nodes
        ]

        if len(references) < 2:
            continue

        direction = is_oneway(tags)
        speed_kph = parse_speed(tags.get("maxspeed"), highway)

        for index in range(len(references) - 1):
            a = references[index]
            b = references[index + 1]

            node_a = osm_nodes[a]
            node_b = osm_nodes[b]

            distance = haversine_distance(
                node_a["latitude"],
                node_a["longitude"],
                node_b["latitude"],
                node_b["longitude"],
            )

            if distance <= 0:
                continue

            travel_time = distance / (speed_kph * 1000 / 3600)

            base_edge = {
                "distance_m": round(distance, 2),
                "road_type": highway,
                "speed_kph": speed_kph,
                "base_travel_time_s": round(travel_time, 2),
            }

            if direction == "forward":
                edges.append({
                    "source": a,
                    "target": b,
                    **base_edge,
                    "one_way": True,
                })
                used_nodes.update([a, b])

            elif direction == "reverse":
                edges.append({
                    "source": b,
                    "target": a,
                    **base_edge,
                    "one_way": True,
                })
                used_nodes.update([a, b])

            else:
                edges.append({
                    "source": a,
                    "target": b,
                    **base_edge,
                    "one_way": False,
                })

                edges.append({
                    "source": b,
                    "target": a,
                    **base_edge,
                    "one_way": False,
                })

                used_nodes.update([a, b])

    # Keep only nodes that belong to the processed road graph.
    graph_nodes = {
        node_id: osm_nodes[node_id]
        for node_id in used_nodes
    }

    NODES_FILE.parent.mkdir(parents=True, exist_ok=True)

    with NODES_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            list(graph_nodes.values()),
            file,
            indent=2,
        )

    with EDGES_FILE.open("w", encoding="utf-8") as file:
        json.dump(edges, file, indent=2)

    print(f"Graph nodes: {len(graph_nodes)}")
    print(f"Graph edges: {len(edges)}")
    print(f"Saved: {NODES_FILE}")
    print(f"Saved: {EDGES_FILE}")


if __name__ == "__main__":
    main()