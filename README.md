# Member 1 - OSM Data Pipeline

## Overview

This module is responsible for obtaining real-world road network data from OpenStreetMap (OSM) and converting it into a clean road graph for the Smart Emergency Ambulance Route Optimizer.

The generated routing graph will be used by Member 2 for the A* pathfinding algorithm.

## Workflow

OpenStreetMap Road Network
        ↓
Download Road Data
        ↓
Process Nodes
        ↓
Process Edges
        ↓
Calculate Road Distances
        ↓
Create Directed Road Graph
        ↓
Validate Graph
        ↓
Save Routing Graph

## Area Used

The road network was obtained for:

Adyar, Chennai, India

## Data Generated

### nodes.csv

Contains information about road network nodes.

Columns:

- `id` - Unique OSM node ID
- `latitude` - Latitude of the node
- `longitude` - Longitude of the node

### edges.csv

Contains information about road connections.

Columns:

- `from` - Starting node
- `to` - Destination node
- `distance` - Road distance in meters
- `road_type` - Type/classification of road
- `road_name` - Name of the road
- `oneway` - Whether the road connection is one-way

### road_network.graphml

Original OSM road network saved in GraphML format.

### routing_graph.graphml

Clean directed routing graph created from the processed nodes and edges.

This is the main output provided to Member 2 for route calculation.

## Graph Statistics

- Nodes: 5,491
- Edges: 13,475
- Connected components: 1
- Invalid edge distances: 0
- Missing node data: 0

## Files

```text
member-1-osm/
│
├── data/
│   ├── nodes.csv
│   ├── edges.csv
│   ├── road_network.graphml
│   └── routing_graph.graphml
│
├── osm_pipeline.py
├── create_graph.py
├── test_route.py
├── README.md
└── .gitignore