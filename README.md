# AstraNav — Graph-Based Campus Navigation

AstraNav is an educational campus navigation web application that visualizes and compares shortest-path algorithms using a C++17 graph engine.

## Features

- Interactive map with source and destination selection.
- Shortest-path calculation using Dijkstra's and A* algorithms.
- Route visualization on a Leaflet map.
- Displays route distance, explored nodes, and execution time.
- FastAPI backend integrated with a C++ algorithm engine.

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript, Leaflet
- **Backend:** Python, FastAPI
- **Algorithm Engine:** C++17
- **Graph Data:** JSON

## Algorithms

- **Dijkstra's Algorithm:** Finds shortest paths using a greedy approach.
- **A* Algorithm:** Uses Haversine distance as a heuristic to guide the search.

## Requirements

- Python 3.10+
- C++17 compiler (`g++`)
- Internet connection for map tiles

## Installation & Setup

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r backend\requirements.txt

g++ -std=c++17 -O2 cpp-engine\src\main.cpp -o cpp-engine\route_engine.exe

python -m uvicorn backend.main:app --reload
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r backend/requirements.txt

g++ -std=c++17 -O2 cpp-engine/src/main.cpp -o cpp-engine/route_engine

python3 -m uvicorn backend.main:app --reload
```

Open the application using the local frontend setup provided in the project.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Check backend status |
| GET | `/api/graph` | Retrieve graph data |
| POST | `/api/route` | Calculate shortest path |
| GET | `/docs` | API documentation |

## Project Structure

```text
AstraNav/
├── backend/
├── cpp-engine/
├── frontend/
├── tests/
└── README.md
```

## DAA Concepts

- Graph representation using adjacency lists
- Greedy algorithm
- Heuristic search
- Edge relaxation
- Path reconstruction
- Time and space complexity analysis

## Limitations

- Campus nodes, coordinates, and edge weights are illustrative and not verified real-world navigation data.
- OpenStreetMap provides the visual map background, not the routing graph.
- Execution times on small graphs may vary and should not be treated as reliable benchmarks.

---

**AstraNav** — Exploring shortest paths through graph algorithms.