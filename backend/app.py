import sys
import json
import os
from pathlib import Path

# --------------------------------------------------
# Project root
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Allow Python to find the "scripts" folder
sys.path.insert(0, str(PROJECT_ROOT))


# --------------------------------------------------
# Imports
# --------------------------------------------------

from flask import Flask, jsonify, request

from scripts.routing.astar import load_graph, a_star
from scripts.traffic.traffic_simulator import TrafficSimulator


# --------------------------------------------------
# Data paths
# --------------------------------------------------

LOCATIONS_FILE = PROJECT_ROOT / "data" / "locations" / "locations.json"
EDGES_FILE = PROJECT_ROOT / "data" / "processed" / "edges.json"


# --------------------------------------------------
# Use project root for A* relative paths
# --------------------------------------------------

os.chdir(PROJECT_ROOT)


# --------------------------------------------------
# Flask application
# --------------------------------------------------

app = Flask(__name__)


# --------------------------------------------------
# Load graph
# --------------------------------------------------

nodes, graph = load_graph()


# --------------------------------------------------
# Traffic simulator
# --------------------------------------------------

traffic_simulator = TrafficSimulator(
    edges_file=str(EDGES_FILE),
    seed=42
)


# --------------------------------------------------
# Load locations
# --------------------------------------------------

with open(LOCATIONS_FILE, "r", encoding="utf-8") as file:
    locations = json.load(file)


# ==================================================
# API 1: Home
# ==================================================

@app.route("/")
def home():
    return "Ambulance Route Optimiser Backend is running!"


# ==================================================
# API 2: Health check
# ==================================================

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "ambulance-route-optimiser-backend"
    })


# ==================================================
# API 3: Get current traffic
# ==================================================

@app.route("/traffic", methods=["GET"])
def traffic():

    routing_state = traffic_simulator.get_routing_state()

    # Convert tuple keys to strings for JSON
    traffic_conditions = {
        f"{edge[0]}-{edge[1]}": condition
        for edge, condition in routing_state["traffic_conditions"].items()
    }

    # Convert blocked edge tuples to strings
    blocked_edges = [
        f"{edge[0]}-{edge[1]}"
        for edge in routing_state["blocked_edges"]
    ]

    return jsonify({
        "traffic_conditions": traffic_conditions,
        "blocked_edges": blocked_edges
    })


# ==================================================
# API 4: Update traffic condition
# ==================================================

@app.route("/traffic/update", methods=["POST"])
def update_traffic():

    data = request.get_json(silent=True) or {}

    start_node = data.get("start_node")
    end_node = data.get("end_node")
    condition = data.get("condition")

    # --------------------------------------------------
    # Check required fields
    # --------------------------------------------------

    if start_node is None or end_node is None or condition is None:
        return jsonify({
            "error": "start_node, end_node and condition are required."
        }), 400

    # --------------------------------------------------
    # Allowed traffic conditions
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Keep node IDs as strings
    #
    # edges.json stores node IDs as strings.
    # Do not convert them to integers.
    # --------------------------------------------------

    start_node = str(start_node)
    end_node = str(end_node)

    # --------------------------------------------------
    # Update traffic
    # --------------------------------------------------

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


# ==================================================
# API 5: Calculate ambulance route
# ==================================================

@app.route("/route", methods=["POST"])
def route():

    data = request.get_json(silent=True) or {}

    start = data.get("start")
    destination = data.get("destination")

    # --------------------------------------------------
    # Check required fields
    # --------------------------------------------------

    if not start or not destination:
        return jsonify({
            "error": "Both 'start' and 'destination' are required."
        }), 400

    # --------------------------------------------------
    # Check start location
    # --------------------------------------------------

    if start not in locations:
        return jsonify({
            "error": f"Unknown start location '{start}'."
        }), 400

    # --------------------------------------------------
    # Check destination
    # --------------------------------------------------

    if destination not in locations:
        return jsonify({
            "error": f"Unknown destination location '{destination}'."
        }), 400

    # --------------------------------------------------
    # Get graph node IDs
    # --------------------------------------------------

    start_node = locations[start]["graph_node_id"]
    destination_node = locations[destination]["graph_node_id"]

    # --------------------------------------------------
    # Get current traffic state
    # --------------------------------------------------

    routing_state = traffic_simulator.get_routing_state()

    # --------------------------------------------------
    # Run A* algorithm
    # --------------------------------------------------

    path, total_time = a_star(
        graph,
        nodes,
        start_node,
        destination_node,
        blocked_edges=routing_state["blocked_edges"],
        traffic_conditions=routing_state["traffic_conditions"]
    )

    # --------------------------------------------------
    # Check if route was found
    # --------------------------------------------------

    if path is None:
        return jsonify({
            "error": "No valid route found.",
            "start": start,
            "destination": destination
        }), 404

    # --------------------------------------------------
    # Return route result
    # --------------------------------------------------

    return jsonify({
        "start": start,
        "destination": destination,
        "start_node": start_node,
        "destination_node": destination_node,
        "path": path,
        "total_time_seconds": total_time
    })


# ==================================================
# Start Flask server
# ==================================================

if __name__ == "__main__":
    app.run(debug=True)