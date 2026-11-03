# AstraNav — Graph-Based Campus Navigation

AstraNav is a graph-based campus navigation web application that demonstrates shortest-path algorithms using a **C++17 algorithm engine**, **Python FastAPI backend**, and an interactive web interface.

It models campus locations as vertices and pedestrian connections as weighted edges, allowing users to calculate, visualize, and compare shortest routes between locations.

## Key Features

- **Interactive Campus Map:** Select source and destination locations.
- **Shortest-Path Algorithms:** Calculate routes using Dijkstra's and Bidirectional Dijkstra algorithms.
- **Route Visualization:** Display the calculated path over the campus map using SVG.
- **Algorithm Comparison:** View explored nodes and execution time.
- **Distance Calculation:** Display the total route weight.
- **C++ Integration:** Execute graph algorithms through a compiled C++17 engine.
- **Centralized Graph Data:** Store campus locations and connections in JSON.
- **REST API:** Communicate between the frontend and algorithm engine through FastAPI.

## Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, FastAPI |
| Algorithm Engine | C++17 |
| Graph Storage | JSON |
| Visualization | SVG |
| API Server | Uvicorn |

## Algorithms Implemented

### 1. Dijkstra's Algorithm

Dijkstra's Algorithm is a greedy shortest-path algorithm that finds the minimum-cost path from a source vertex to other reachable vertices in a weighted graph with non-negative edge weights.

**Approach:**
1. Initialize the source distance to zero and all other distances to infinity.
2. Select the unvisited vertex with the smallest tentative distance using a priority queue.
3. Relax its adjacent edges.
4. Update distances and parent information when a shorter path is found.
5. Reconstruct the shortest path using the parent information.

**Time Complexity:** \(O((V+E)\log V)\) using an adjacency list and priority queue.

### 2. Bidirectional Dijkstra

Bidirectional Dijkstra performs two simultaneous shortest-path searches:

- A forward search from the source.
- A backward search from the destination.

The searches meet in the graph, allowing the algorithm to determine the shortest route while potentially exploring fewer vertices than a conventional one-directional search.

**Time Complexity:** \(O((V+E)\log V)\) as a worst-case upper bound.

The actual performance improvement depends on the graph structure and search conditions.

## System Architecture

```text
             User
              |
              v
      Frontend (HTML/CSS/JS)
              |
              | HTTP Request
              v
       FastAPI Backend
              |
              | Load Graph / Validate Request
              v
          graph.json
              |
              v
       C++17 Algorithm Engine
              |
        +-----+------+
        |            |
        v            v
     Dijkstra   Bidirectional
                  Dijkstra
        |            |
        +-----+------+
              |
              v
       Route + Metrics
              |
              v
        FastAPI Backend
              |
              v
       Frontend Visualization
```

## How It Works

1. The frontend retrieves campus graph data from the FastAPI backend.
2. The user selects a source and destination.
3. The frontend sends a route request to the backend.
4. FastAPI validates the request and invokes the C++17 executable.
5. The C++ engine executes the selected shortest-path algorithm.
6. The engine returns the calculated path and performance metrics.
7. The backend validates and returns the result.
8. JavaScript visualizes the route on the campus map using an SVG overlay.

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

## Installation and Setup

### Prerequisites

Make sure you have installed:

- Python 3.10 or higher
- C++17 compatible compiler (`g++`)
- pip
- Git (optional, for cloning the repository)

### Windows (PowerShell)

Run the following commands from the project root directory:

```powershell
# Create a virtual environment
py -m venv .venv

# Activate the environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend\requirements.txt

# Compile the C++ algorithm engine
g++ -std=c++17 -O2 -Wall -Wextra -pedantic cpp-engine\src\main.cpp -o cpp-engine\route_engine.exe

# Start the FastAPI server
python -m uvicorn backend.main:app --reload
```

### Linux / macOS

```bash
# Create a virtual environment
python3 -m venv .venv

# Activate the environment
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Compile the C++ algorithm engine
g++ -std=c++17 -O2 -Wall -Wextra -pedantic cpp-engine/src/main.cpp -o cpp-engine/route_engine

# Start the FastAPI server
python3 -m uvicorn backend.main:app --reload
```

## Access the Application

After starting the FastAPI server, open:

- **Application:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **API Documentation (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

The backend serves both the frontend and API, so a separate frontend development server is not required.

> These are local development URLs. They work while the server is running on your machine.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Serves the frontend application |
| GET | `/api/health` | Checks backend and engine status |
| GET | `/api/graph` | Retrieves campus graph data |
| POST | `/api/route` | Calculates a shortest path |
| GET | `/docs` | Interactive API documentation |

## Graph Representation

The campus is represented as a weighted graph:

\[
G=(V,E)
\]

Where:

- \(V\) represents campus locations (vertices).
- \(E\) represents pedestrian connections (edges).
- \(w(u,v)\) represents the weight of the connection between two vertices.

The graph is stored in `cpp-engine/data/graph.json` and loaded by the backend.

**Current graph statistics:**

| Metric | Value |
|---|---:|
| Vertices | 36 |
| Edges | 39 |
| Graph Type | Weighted, undirected |
| Storage Format | JSON |
| Edge Weights | Illustrative kilometres |

## Testing and Validation

The project includes graph validation tests and an algorithm comparison report.

The two algorithms were tested across all **1,260 ordered source-destination pairs** in the supplied graph.

| Validation | Result |
|---|---|
| Reachability mismatches | 0 |
| Shortest-distance mismatches | 0 |
| Ordered source-destination pairs tested | 1,260 |
| C++ compilation | Passed |
| Frontend JavaScript syntax check | Passed |
| FastAPI endpoint checks | Passed |

For detailed results, see [`tests/TEST_REPORT.md`](tests/TEST_REPORT.md).

## DAA Concepts Demonstrated

- Graph theory and adjacency lists
- Weighted and undirected graphs
- Greedy algorithm design
- Bidirectional search
- Priority queues
- Edge relaxation
- Shortest-path reconstruction
- Time and space complexity analysis
- Algorithm performance comparison

## Limitations

- Campus nodes, coordinates, and edge weights are illustrative and have not been independently verified against actual pedestrian routes.
- The campus map is used as a visual background; route calculation is performed using the JSON graph.
- The current graph represents the supplied campus connections and may not include every real-world pedestrian walkway.
- Execution times on small graphs vary and should not be treated as reliable benchmarks.
- Bidirectional Dijkstra does not guarantee fewer explored nodes for every source-destination pair.

## Future Improvements

- Verify campus coordinates and walking distances against actual campus paths.
- Expand the graph to cover additional campus locations and pedestrian connections.
- Add route alternatives and improved route comparison.
- Introduce accessibility-aware routing and obstacle handling.
- Improve algorithm benchmarking using larger graphs.

---

**AstraNav — Exploring shortest paths through graph algorithms.**