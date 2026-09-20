import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(PROJECT_ROOT))

from scripts.routing.astar import load_graph, a_star
from scripts.traffic.traffic_simulator import TrafficSimulator


def main():
    # Load the existing road graph.
    nodes, graph = load_graph()

    print(f"Loaded {len(nodes)} nodes.")
    print(
        f"Loaded "
        f"{sum(len(edges) for edges in graph.values())} "
        f"directed edges."
    )

    # Create the Member 3 traffic simulator.
    simulator = TrafficSimulator(seed=42)

    # P1 -> H1 from locations.json.
    start = "10100613692"
    goal = "7424464489"

    print()
    print(f"Start node: {start}")
    print(f"Goal node: {goal}")

    # ---------------------------------------------------------
    # TEST 1: Normal traffic
    # ---------------------------------------------------------

    normal_state = simulator.get_routing_state()

    normal_path, normal_time = a_star(
        graph,
        nodes,
        start,
        goal,
        blocked_edges=normal_state["blocked_edges"],
        traffic_conditions=normal_state["traffic_conditions"],
    )

    if normal_path is None:
        print("No route found under normal traffic.")
        return

    print()
    print("Normal traffic:")
    print(f"Route nodes: {len(normal_path)}")
    print(f"Travel time: {normal_time:.2f} seconds")

    # ---------------------------------------------------------
    # TEST 2: Heavy traffic on every edge of the normal route
    # ---------------------------------------------------------

    for source, target in zip(normal_path, normal_path[1:]):
        simulator.set_traffic(
            source,
            target,
            "heavy"
        )

    heavy_state = simulator.get_routing_state()

    heavy_path, heavy_time = a_star(
        graph,
        nodes,
        start,
        goal,
        blocked_edges=heavy_state["blocked_edges"],
        traffic_conditions=heavy_state["traffic_conditions"],
    )

    if heavy_path is None:
        print("No route found under heavy traffic.")
        return

    print()
    print("Heavy traffic on the original route:")
    print(f"Route nodes: {len(heavy_path)}")
    print(f"Travel time: {heavy_time:.2f} seconds")

    # ---------------------------------------------------------
    # TEST 3: Block one edge from the original route
    # ---------------------------------------------------------

    blocked_source = normal_path[0]
    blocked_target = normal_path[1]

    simulator.block_edge(
        blocked_source,
        blocked_target
    )

    blocked_state = simulator.get_routing_state()

    blocked_path, blocked_time = a_star(
        graph,
        nodes,
        start,
        goal,
        blocked_edges=blocked_state["blocked_edges"],
        traffic_conditions=blocked_state["traffic_conditions"],
    )

    print()
    print("Road closure test:")
    print(
        f"Blocked edge: "
        f"{blocked_source} -> {blocked_target}"
    )

    if blocked_path is None:
        print("No alternate route found after blocking the edge.")
        print("Closure was successfully passed to A*.")
    else:
        blocked_edge_used = any(
            source == blocked_source
            and target == blocked_target
            for source, target in zip(
                blocked_path,
                blocked_path[1:]
            )
        )

        print(
            f"Route nodes after closure: "
            f"{len(blocked_path)}"
        )
        print(
            f"Travel time after closure: "
            f"{blocked_time:.2f} seconds"
        )

        if blocked_edge_used:
            print(
                "ERROR: A* returned a route containing "
                "the blocked directed edge."
            )
            return

        print(
            "Closure test passed: "
            "A* avoided the blocked directed edge."
        )

    # ---------------------------------------------------------
    # Compare traffic results
    # ---------------------------------------------------------

    print()
    print("Traffic comparison:")
    print(
        f"Normal travel time: "
        f"{normal_time:.2f} seconds"
    )
    print(
        f"Heavy traffic travel time: "
        f"{heavy_time:.2f} seconds"
    )
    print(
        f"Heavy traffic difference: "
        f"{heavy_time - normal_time:.2f} seconds"
    )


if __name__ == "__main__":
    main()