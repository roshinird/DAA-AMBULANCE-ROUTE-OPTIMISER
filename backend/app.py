import sys
import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, jsonify, request

from scripts.routing.astar import load_graph, a_star
from scripts.traffic.traffic_simulator import TrafficSimulator

LOCATIONS_FILE = PROJECT_ROOT / "data" / "locations" / "locations.json"
EDGES_FILE = PROJECT_ROOT / "data" / "processed" / "edges.json"

os.chdir(PROJECT_ROOT)

app = Flask(__name__)

nodes, graph = load_graph()

traffic_simulator = TrafficSimulator(
    edges_file=str(EDGES_FILE),
    seed=42
)

with open(LOCATIONS_FILE, "r", encoding="utf-8") as file:
    locations = json.load(file)


@app.route("/")
def home():
    return "Ambulance Route Optimiser Backend is running!"


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "ambulance-route-optimiser-backend"
    })


@app.route("/traffic", methods=["GET"])
def traffic():
    routing_state = traffic_simulator.get_routing_state()

    traffic_conditions = {
        f"{edge[0]}-{edge[1]}": condition
        for edge, condition in routing_state["traffic_conditions"].items()
    }

    blocked_edges = [
        f"{edge[0]}-{edge[1]}"
        for edge in routing_state["blocked_edges"]
    ]

    return jsonify({
        "traffic_conditions": traffic_conditions,
        "blocked_edges": blocked_edges
    })


@app.route("/traffic/update", methods=["POST"])
def update_traffic():
    data = request.get_json(silent=True) or {}

    start_node = data.get("start_node")
    end_node = data.get("end_node")
    condition = data.get("condition")

    if start_node is None or end_node is None or condition is None:
        return jsonify({
            "error": "start_node, end_node and condition are required."
        }), 400

    allowed_conditions = {
        "normal",
        "light",
        "moderate",
        "heavy"
    }

    if condition not in allowed_conditions:
        return jsonify({
            "error": "Invalid traffic condition.",
            "allowed_conditions": sorted(allowed_conditions)
        }), 400

    start_node = str(start_node)
    end_node = str(end_node)

    try:
        traffic_simulator.set_traffic(
            start_node,
            end_node,
            condition
        )
    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    return jsonify({
        "message": "Traffic condition updated successfully.",
        "start_node": start_node,
        "end_node": end_node,
        "condition": condition
    })


@app.route("/traffic/block", methods=["POST"])
def block_traffic():
    data = request.get_json(silent=True) or {}

    start_node = data.get("start_node")
    end_node = data.get("end_node")

    if start_node is None or end_node is None:
        return jsonify({
            "error": "start_node and end_node are required."
        }), 400

    start_node = str(start_node)
    end_node = str(end_node)

    try:
        traffic_simulator.block_edge(
            start_node,
            end_node
        )
    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    return jsonify({
        "message": "Road blocked successfully.",
        "start_node": start_node,
        "end_node": end_node
    })


@app.route("/route", methods=["POST"])
def route():
    data = request.get_json(silent=True) or {}

    start = data.get("start")
    destination = data.get("destination")

    if not start or not destination:
        return jsonify({
            "error": "Both 'start' and 'destination' are required."
        }), 400

    if start not in locations:
        return jsonify({
            "error": f"Unknown start location '{start}'."
        }), 400

    if destination not in locations:
        return jsonify({
            "error": f"Unknown destination location '{destination}'."
        }), 400

    start_node = locations[start]["graph_node_id"]
    destination_node = locations[destination]["graph_node_id"]

    routing_state = traffic_simulator.get_routing_state()

    path, total_time = a_star(
        graph,
        nodes,
        start_node,
        destination_node,
        blocked_edges=routing_state["blocked_edges"],
        traffic_conditions=routing_state["traffic_conditions"]
    )

    if path is None:
        return jsonify({
            "error": "No valid route found.",
            "start": start,
            "destination": destination
        }), 404

    return jsonify({
        "start": start,
        "destination": destination,
        "start_node": start_node,
        "destination_node": destination_node,
        "path": path,
        "total_time_seconds": total_time
    })


if __name__ == "__main__":
    app.run(debug=True)