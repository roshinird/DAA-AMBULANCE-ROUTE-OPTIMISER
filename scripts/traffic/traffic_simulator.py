import json
import random


EDGES_FILE = "data/processed/edges.json"

TRAFFIC_LEVELS = (
    "normal",
    "light",
    "moderate",
    "heavy",
)


class TrafficSimulator:
    """
    Generate and manage dynamic traffic conditions for graph edges.

    The simulator does not modify the road graph or routing algorithm.
    It only maintains the current dynamic state of directed edges.

    Output is compatible with Member 2's A* routing interface:

        traffic_conditions:
            {(source, target): condition}

        blocked_edges:
            {(source, target)}
    """

    def __init__(self, edges_file=EDGES_FILE, seed=None):
        self.edges_file = edges_file
        self.random = random.Random(seed)

        self.edges = self._load_edges()

        self.traffic_conditions = {}
        self.blocked_edges = set()

        self.reset()

    def _load_edges(self):
        """Load the existing directed road graph."""

        with open(self.edges_file, "r", encoding="utf-8") as file:
            edges = json.load(file)

        return edges

    def reset(self):
        """Reset all roads to normal traffic and no closures."""

        self.traffic_conditions = {
            (edge["source"], edge["target"]): "normal"
            for edge in self.edges
        }

        self.blocked_edges = set()

    def set_traffic(self, source, target, condition):
        """
        Set the traffic condition for one directed edge.
        """

        if condition not in TRAFFIC_LEVELS:
            raise ValueError(
                f"Invalid traffic condition '{condition}'. "
                f"Expected one of: {TRAFFIC_LEVELS}"
            )

        edge_key = (source, target)

        if not self._edge_exists(edge_key):
            raise ValueError(
                f"Directed edge {source} -> {target} does not exist."
            )

        self.traffic_conditions[edge_key] = condition

    def block_edge(self, source, target):
        """Block one directed road segment."""

        edge_key = (source, target)

        if not self._edge_exists(edge_key):
            raise ValueError(
                f"Directed edge {source} -> {target} does not exist."
            )

        self.blocked_edges.add(edge_key)

    def unblock_edge(self, source, target):
        """Remove a closure from one directed road segment."""

        self.blocked_edges.discard((source, target))

    def _edge_exists(self, edge_key):
        """Check whether a directed edge exists in the graph."""

        source, target = edge_key

        return any(
            edge["source"] == source
            and edge["target"] == target
            for edge in self.edges
        )

    def randomize_traffic(self):
        """
        Generate a new traffic condition for every directed edge.

        This creates a simulated traffic snapshot.
        """

        for edge in self.edges:
            edge_key = (
                edge["source"],
                edge["target"],
            )

            self.traffic_conditions[edge_key] = (
                self.random.choice(TRAFFIC_LEVELS)
            )

    def update_traffic(self):
        """
        Advance the simulation by one traffic update.

        Each directed edge receives a new simulated traffic condition.
        Existing road closures are preserved.
        """

        for edge in self.edges:
            edge_key = (
                edge["source"],
                edge["target"],
            )

            self.traffic_conditions[edge_key] = (
                self.random.choice(TRAFFIC_LEVELS)
            )

    def get_traffic_conditions(self):
        """Return the current traffic state."""

        return dict(self.traffic_conditions)

    def get_blocked_edges(self):
        """Return the current blocked-edge state."""

        return set(self.blocked_edges)

    def get_routing_state(self):
        """
        Return the complete dynamic state required by a routing algorithm.
        """

        return {
            "traffic_conditions": self.get_traffic_conditions(),
            "blocked_edges": self.get_blocked_edges(),
        }


if __name__ == "__main__":

    simulator = TrafficSimulator(seed=42)

    first_edge = simulator.edges[0]

    source = first_edge["source"]
    target = first_edge["target"]

    simulator.set_traffic(
        source,
        target,
        "heavy"
    )

    simulator.block_edge(
        source,
        target
    )

    print("Before traffic update:")

    print(
        "Traffic:",
        simulator.traffic_conditions[
            (source, target)
        ]
    )

    print(
        "Blocked:",
        (source, target) in simulator.blocked_edges
    )

    simulator.update_traffic()

    print()
    print("After traffic update:")

    print(
        "Traffic:",
        simulator.traffic_conditions[
            (source, target)
        ]
    )

    print(
        "Blocked:",
        (source, target) in simulator.blocked_edges
    )