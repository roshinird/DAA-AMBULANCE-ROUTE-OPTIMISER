import networkx as nx

# Load the routing graph
G = nx.read_graphml("data/routing_graph.graphml")

# Convert node IDs back to integers
G = nx.relabel_nodes(G, lambda x: int(x))

print("Routing graph loaded successfully!")
print("Nodes:", G.number_of_nodes())
print("Edges:", G.number_of_edges())

# Select two nodes from the graph
nodes = list(G.nodes)

start_node = nodes[0]
end_node = nodes[-1]

print("\nStart node:", start_node)
print("End node:", end_node)

# Find the shortest route using distance
route = nx.shortest_path(
    G,
    source=start_node,
    target=end_node,
    weight="distance"
)

# Calculate total distance
distance = nx.shortest_path_length(
    G,
    source=start_node,
    target=end_node,
    weight="distance"
)

print("\nRoute found successfully!")
print("Number of nodes in route:", len(route))
print("Total distance:", round(distance, 2), "meters")

print("\nFirst few route nodes:")
print(route[:10])