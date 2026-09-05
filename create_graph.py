import pandas as pd
import networkx as nx

# -----------------------------------
# 1. Load nodes and edges
# -----------------------------------

nodes_df = pd.read_csv("data/nodes.csv")
edges_df = pd.read_csv("data/edges.csv")

print("Nodes loaded:", len(nodes_df))
print("Edges loaded:", len(edges_df))


# -----------------------------------
# 2. Validate node data
# -----------------------------------

missing_nodes = nodes_df[
    nodes_df["id"].isnull() |
    nodes_df["latitude"].isnull() |
    nodes_df["longitude"].isnull()
]

print("\nNodes with missing data:", len(missing_nodes))


# -----------------------------------
# 3. Validate edge data
# -----------------------------------

invalid_edges = edges_df[
    edges_df["distance"].isnull() |
    (edges_df["distance"] <= 0)
]

print("Edges with invalid distance:", len(invalid_edges))


# -----------------------------------
# 4. Create directed road graph
# -----------------------------------

G = nx.MultiDiGraph()


# -----------------------------------
# 5. Add nodes
# -----------------------------------

for _, row in nodes_df.iterrows():
    G.add_node(
        int(row["id"]),
        latitude=float(row["latitude"]),
        longitude=float(row["longitude"])
    )


# -----------------------------------
# 6. Add edges
# -----------------------------------

for _, row in edges_df.iterrows():
    G.add_edge(
        int(row["from"]),
        int(row["to"]),
        distance=float(row["distance"]),
        road_type=row["road_type"],
        road_name=row["road_name"],
        oneway=row["oneway"]
    )


# -----------------------------------
# 7. Display graph information
# -----------------------------------

print("\nGraph created successfully!")

print("Number of nodes:", G.number_of_nodes())
print("Number of edges:", G.number_of_edges())


# -----------------------------------
# 8. Check first node and edge
# -----------------------------------

print("\nFirst node:")
print(list(G.nodes(data=True))[0])

print("\nFirst edge:")
print(list(G.edges(data=True))[0])


# -----------------------------------
# 9. Check graph connectivity
# -----------------------------------

components = list(nx.weakly_connected_components(G))

print("\nNumber of connected components:", len(components))

largest_component = max(components, key=len)

print("Nodes in largest component:", len(largest_component))


# -----------------------------------
# 10. Save routing graph
# -----------------------------------

nx.write_graphml(
    G,
    "data/routing_graph.graphml"
)

print("\nRouting graph saved successfully!")
print("Location: data/routing_graph.graphml")