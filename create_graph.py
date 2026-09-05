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
# 2. Create directed road graph
# -----------------------------------

G = nx.MultiDiGraph()


# -----------------------------------
# 3. Add nodes
# -----------------------------------

for _, row in nodes_df.iterrows():
    G.add_node(
        int(row["id"]),
        latitude=row["latitude"],
        longitude=row["longitude"]
    )


# -----------------------------------
# 4. Add edges
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
# 5. Display graph information
# -----------------------------------

print("\nGraph created successfully!")

print("Number of nodes:", G.number_of_nodes())
print("Number of edges:", G.number_of_edges())


# -----------------------------------
# 6. Check first node and edge
# -----------------------------------

print("\nFirst node:")
print(list(G.nodes(data=True))[0])

print("\nFirst edge:")
print(list(G.edges(data=True))[0])


# -----------------------------------
# 7. Save graph
# -----------------------------------

nx.write_graphml(
    G,
    "data/routing_graph.graphml"
)

print("\nRouting graph saved to:")
print("data/routing_graph.graphml")
# -----------------------------------
# 8. Check graph connectivity
# -----------------------------------

components = list(nx.weakly_connected_components(G))

print("\nNumber of connected components:", len(components))

largest_component = max(components, key=len)

print("Nodes in largest component:", len(largest_component))