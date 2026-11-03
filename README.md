# AstraNav — Graph-Based Campus Navigation

AstraNav is an educational campus navigation web application that demonstrates and compares shortest-path algorithms using a **C++17 graph engine**, a **FastAPI backend**, and an interactive web-based campus map.

The project is designed to demonstrate how graph algorithms can be applied to campus navigation by calculating and visualizing routes between selected locations.

## Features

- Interactive campus map with source and destination selection.
- Shortest-path calculation using Dijkstra’s and Bidirectional Dijkstra algorithms.
- Route visualization using an SVG overlay on the campus map.
- Displays route distance, explored nodes, and execution time.
- FastAPI backend integrated with a C++17 algorithm engine.
- Centralized graph data stored in JSON.
- API validation for graph nodes, edges, and calculated routes.

## Tech Stack

| Component | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, FastAPI |
| Algorithm Engine | C++17 |
| Graph Data | JSON |
| Route Visualization | SVG |
| API Server | Uvicorn |

## Algorithms

### 1. Dijkstra’s Algorithm

Dijkstra’s Algorithm is a greedy shortest-path algorithm used to find the minimum-cost path between a source and destination in a weighted graph with non-negative edge weights.

**Working principle:**
- Starts from the selected source node.
- Maintains the shortest known distance to each node.
- Selects the unvisited node with the minimum tentative distance.
- Relaxes its adjacent edges.
- Continues until the destination is reached or no reachable nodes remain.

**Time Complexity:** \(O((V+E)\log V)\) using a priority queue and adjacency list.

### 2. Bidirectional Dijkstra’s Algorithm

Bidirectional Dijkstra improves the search process by running two Dijkstra searches simultaneously:

- Forward search starts from the source.
- Backward search starts from the destination.
- Both searches expand through the graph.
- The algorithm identifies the best connecting route between the two searches.

It can reduce the explored search space in suitable graphs, although the actual performance depends on graph structure and implementation.

**Time Complexity:** \(O((V+E)\log V)\) as a worst-case upper bound.

## Requirements

- Python 3.10 or higher.
- C++17 compatible compiler (`g++`).
- pip package manager.
- Internet connection if external map resources are used.

## Installation & Setup

### Windows (PowerShell)

Run these commands from the project root directory:

```powershell
# Create a virtual environment
py -m venv .venv

# Activate the environment
.\.venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r backend\requirements.txt

# Compile the C++ algorithm engine
g++ -std=c++17 -O2 -Wall -Wextra -pedantic cpp-engine\src\main.cpp -o cpp-engine\route_engine.exe

# Start the FastAPI server
python -m uvicorn backend.main:app --reload
```

### Linux / macOS

Run these commands from the project root directory:

```bash
# Create a virtual environment
python3 -m venv .venv

# Activate the environment
source .venv/bin/activate

# Install Python dependencies
pip install -r backend/requirements.txt

# Compile the C++ algorithm engine
g++ -std=c++17 -O2 -Wall -Wextra -pedantic cpp-engine/src/main.cpp -o cpp-engine/route_engine

# Start the FastAPI server
python3 -m uvicorn backend.main:app --reload
```

## Access the Application

After starting the FastAPI server, open:

**Application:** http://127.0.0.1:8000

**API Documentation:** http://127.0.0.1:8000/docs

The FastAPI backend serves the frontend and API from the same application, so a separate frontend development server is not required.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Serves the frontend application |
| GET | `/api/health` | Checks backend and engine status |
| GET | `/api/graph` | Retrieves campus graph data |
| POST | `/api/route` | Calculates a shortest path |
| GET | `/docs` | Opens interactive API documentation |

## Project Structure

```text
AstraNav/
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   └── requirements.txt
│
├── cpp-engine/
│   ├── data/
│   │   └── graph.json
│   └── src/
│       └── main.cpp
│
├── frontend/
│   ├── campus-map.png
│   ├── index.html
│   ├── app.js
│   └── style.css
│
├── tests/
│   ├── test_graph.py
│   └── TEST_REPORT.md
│
├── .gitignore
└── README.md
```

## How It Works

1. The frontend loads the campus graph from the FastAPI backend.
2. The user selects a source and destination.
3. The frontend sends a route calculation request to the backend.
4. FastAPI validates the request and invokes the compiled C++ engine.
5. The C++ engine executes the selected shortest-path algorithm.
6. The calculated path and performance information are returned to the frontend.
7. JavaScript displays the route on the campus map using an SVG overlay.

## DAA Concepts Demonstrated

- Graph representation using adjacency lists.
- Weighted and undirected graphs.
- Greedy algorithm design.
- Bidirectional search.
- Edge relaxation.
- Priority queues.
- Path reconstruction.
- Time and space complexity analysis.

## Testing

The project includes graph validation tests and an algorithm comparison report.

The supplied graph contains:
- 36 vertices (campus locations).
- 39 edges (connections).

The two algorithms were compared across all 1,260 ordered source-destination pairs with no shortest-distance mismatches in the tested graph.

Refer to `tests/TEST_REPORT.md` for the detailed validation results.

## Limitations

- Campus nodes, coordinates, and edge weights are illustrative and have not been independently verified against actual walking distances.
- The campus map is used as a visual background; routing is performed using the JSON graph, not by a map provider.
- The graph currently models the supplied connections and does not guarantee that every real-world pedestrian walkway is represented.
- Execution times on small graphs can vary and should not be treated as reliable performance benchmarks.
- Bidirectional Dijkstra's performance advantage depends on the graph structure and search conditions.

---

**AstraNav — Exploring shortest paths through graph algorithms.**