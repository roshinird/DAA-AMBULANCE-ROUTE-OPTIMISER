import json
import matplotlib.pyplot as plt

NODES_FILE = "data/processed/nodes.json"
EDGES_FILE = "data/processed/edges.json"
LOCATIONS_FILE = "data/locations/locations.json"
OUTPUT_FILE = "docs/osm-graph-preview.png"

print("Loading graph...")

with open(NODES_FILE, "r", encoding="utf-8") as f:
    nodes = json.load(f)

with open(EDGES_FILE, "r", encoding="utf-8") as f:
    edges = json.load(f)

with open(LOCATIONS_FILE, "r", encoding="utf-8") as f:
    locations = json.load(f)

node_lookup = {
    str(node["id"]): node
    for node in nodes
}

print(f"Nodes: {len(nodes)}")
print(f"Edges: {len(edges)}")

fig, ax = plt.subplots(figsize=(12, 10))

# Draw road edges
for edge in edges:
    source = node_lookup.get(str(edge["source"]))
    target = node_lookup.get(str(edge["target"]))

    if source is None or target is None:
        continue

    ax.plot(
        [source["longitude"], target["longitude"]],
        [source["latitude"], target["latitude"]],
        linewidth=0.4,
        alpha=0.5
    )

# Draw the five selected locations
for location_id, location in locations.items():
    ax.scatter(
        location["longitude"],
        location["latitude"],
        s=80,
        zorder=5
    )

    ax.annotate(
        location_id,
        (
            location["longitude"],
            location["latitude"]
        ),
        xytext=(6, 6),
        textcoords="offset points",
        fontsize=10,
        fontweight="bold"
    )

ax.set_title("Koramangala OSM Road Network - Member 1 Graph Preview")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_aspect("equal")

plt.tight_layout()

plt.savefig(
    OUTPUT_FILE,
    dpi=200,
    bbox_inches="tight"
)

plt.show()

print(f"\nSaved graph preview to: {OUTPUT_FILE}")