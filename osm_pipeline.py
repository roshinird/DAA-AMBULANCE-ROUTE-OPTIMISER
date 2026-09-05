import osmnx as ox
import pandas as pd

# -----------------------------------
# 1. Download OSM road network
# -----------------------------------

place = "Adyar, Chennai, India"

print("Downloading road network...")

G = ox.graph.graph_from_place(
    place,
    network_type="drive"
)

print("Road network downloaded successfully!")
print("Number of nodes:", len(G.nodes))
print("Number of edges:", len(G.edges))


# -----------------------------------
# 2. Display first node and edge
# -----------------------------------

print("\nFirst node:")
print(list(G.nodes(data=True))[0])

print("\nFirst edge:")
print(list(G.edges(data=True))[0])


# -----------------------------------
# 3. Process nodes
# -----------------------------------

nodes = []

for node_id, data in G.nodes(data=True):
    nodes.append({
        "id": node_id,
        "latitude": data["y"],
        "longitude": data["x"]
    })

print("\nTotal processed nodes:", len(nodes))
print("First processed node:", nodes[0])


# -----------------------------------
# 4. Process edges
# -----------------------------------

edges = []

for u, v, data in G.edges(data=True):
    edges.append({
        "from": u,
        "to": v,
        "distance": float(data["length"]),
        "road_type": data.get("highway"),
        "road_name": data.get("name"),
        "oneway": data.get("oneway")
    })

print("\nTotal processed edges:", len(edges))
print("First processed edge:", edges[0])


# -----------------------------------
# 5. Check invalid distances
# -----------------------------------

invalid_edges = [
    edge for edge in edges
    if edge["distance"] <= 0
]

print("\nEdges with invalid distances:", len(invalid_edges))


# -----------------------------------
# 6. Save nodes
# -----------------------------------

nodes_df = pd.DataFrame(nodes)

nodes_df.to_csv(
    "data/nodes.csv",
    index=False
)

print("\nNodes saved to data/nodes.csv")


# -----------------------------------
# 7. Save edges
# -----------------------------------

edges_df = pd.DataFrame(edges)

edges_df.to_csv(
    "data/edges.csv",
    index=False
)

print("\nEdges saved to data/edges.csv")


# -----------------------------------
# 8. Save complete road graph
# -----------------------------------

graph_path = "data/road_network.graphml"

ox.io.save_graphml(
    G,
    graph_path
)

print("\nRoad graph saved to data/road_network.graphml")


# -----------------------------------
# 9. Test saved graph
# -----------------------------------

loaded_graph = ox.io.load_graphml(
    "data/road_network.graphml"
)

print("\nSaved graph loaded successfully!")

print("Loaded nodes:", len(loaded_graph.nodes))
print("Loaded edges:", len(loaded_graph.edges))