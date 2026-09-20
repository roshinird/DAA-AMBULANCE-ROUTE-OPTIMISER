# OSM Data Pipeline

## 1. Overview

This document describes the OpenStreetMap (OSM) data pipeline developed for the Ambulance Route Optimizer project.

The pipeline converts a small real-world road network in Koramangala, Bengaluru into a lightweight graph that can be used by the route-finding component.

Pipeline:

OpenStreetMap
→ Selected geographic area
→ Road network extraction
→ Clean graph
→ Patient/hospital location mapping
→ Graph data for A*

---

## 2. Selected Geographic Area

The selected area is:

**Koramangala, Bengaluru, Karnataka, India**

The OSM map data was downloaded for a small bounding box covering the selected road network:

- Minimum longitude: 77.616
- Minimum latitude: 12.919
- Maximum longitude: 77.640
- Maximum latitude: 12.937

The area was intentionally kept small to reduce processing time and repository size while containing all required patient and hospital locations.

---

## 3. Data Source

The road network data was obtained from:

**OpenStreetMap (OSM)**

The raw OSM XML file is stored locally as:

`data/raw/koramangala.osm`

The raw file is excluded from Git using `.gitignore` because large raw map files are not required in the repository.

---

## 4. Patient Locations

Three real-world patient locations were selected.

| ID | Name | Latitude | Longitude |
|---|---|---:|---:|
| P1 | Raheja Residency Apartments | 12.928343 | 77.6317673 |
| P2 | Wild Grass Apartments | 12.9330438 | 77.6372421 |
| P3 | KSRP Senior Officer's Residential Quarters | 12.9235398 | 77.6219385 |

These locations are selectable patient starting points for the ambulance routing system.

---

## 5. Hospital Locations

Two real-world hospitals were selected.

| ID | Name | Latitude | Longitude |
|---|---|---:|---:|
| H1 | St. John's Medical College Hospital | 12.9296784 | 77.6183585 |
| H2 | Apollo Spectra Hospitals | 12.9338175 | 77.6201615 |

These locations are selectable ambulance destinations.

---

## 6. Graph Structure

The OSM road network is converted into a directed graph.

### Nodes

Graph nodes represent points from the road network.

Each node contains:

- `id`
- `latitude`
- `longitude`

### Edges

Graph edges represent road connections between nodes.

Each edge contains:

- `source`
- `target`
- `distance`
- `road_type`
- `one_way`
- `speed`
- `base_travel_time`

The graph uses directed edges so that one-way roads can be represented correctly.

For two-way roads, connections are created in both directions.

---

## 7. Road Types

The pipeline processes the following drivable OSM highway types:

- motorway
- trunk
- primary
- secondary
- tertiary
- unclassified
- residential
- living_street
- service

Base speeds are assigned according to road type when a usable OSM speed value is not available.

---

## 8. Graph Processing Procedure

The graph is generated using:

`scripts/osm/build_graph.py`

The processing steps are:

1. Read the raw OSM XML file.
2. Load OSM nodes and their coordinates.
3. Identify drivable road ways.
4. Extract consecutive road-node pairs.
5. Calculate road-segment distances using geographic coordinates.
6. Determine road direction using OSM one-way information.
7. Calculate base travel time using distance and speed.
8. Generate directed graph edges.
9. Save the processed graph as JSON.

The generated files are:

- `data/processed/nodes.json`
- `data/processed/edges.json`

---

## 9. Generated Graph

The current processed graph contains:

- **3,683 graph nodes**
- **7,556 directed graph edges**

The graph is significantly smaller than the raw OSM dataset and is suitable for use by the route-finding component.

---

## 10. Location-to-Node Mapping

The five selectable locations are mapped to nearby graph nodes.

The mapping is performed using:

`scripts/osm/map_locations.py`

The nearest suitable graph node is identified using geographic distance.

### Mapping Results

| Location | Graph Node | Distance |
|---|---:|---:|
| P1 | 10100613692 | 20.60 m |
| P2 | 12183466002 | 15.06 m |
| P3 | 7488258454 | 21.49 m |
| H1 | 7424464489 | 37.17 m |
| H2 | 363763159 | 20.68 m |

The mapping information is stored in:

`data/locations/locations.json`

Each location contains its original coordinates as well as the corresponding `graph_node_id`.

---

## 11. Validation

Graph validation is performed using:

`scripts/osm/validate_graph.py`

The validation checks whether all required patient-to-hospital combinations are reachable.

The following six combinations were tested:

- P1 → H1
- P1 → H2
- P2 → H1
- P2 → H2
- P3 → H1
- P3 → H2

All six routes were found to be reachable.

### Validation Result

**PASS: All 6 patient → hospital routes are reachable.**

---

## 12. Output for Other Project Components

The Member 1 pipeline provides the following processed data:

```text
data/
├── processed/
│   ├── nodes.json
│   └── edges.json
│
└── locations/
    └── locations.json