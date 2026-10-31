# MiniMap — DAA Shortest-Path Explorer

An educational web app that visualizes shortest paths on a small road-like graph and compares **your own C++ implementations** of Dijkstra and A*.

## Included
- Interactive Leaflet map with selectable source/destination.
- Eight illustrative demo nodes centered near SRM University-AP (approximate campus reference: 16.4632, 80.5064). **Node offsets and edges are illustrative, not verified building or road locations.**
- C++17 graph engine implementing Dijkstra and A*.
- FastAPI backend invoking the compiled C++ engine.
- Route distance, explored-node count, engine execution time, and route visualization.

## Requirements
- Python 3.10+
- C++17 compiler (`g++` recommended)
- Internet access for Leaflet and OpenStreetMap map tiles.

## Run on Windows (PowerShell)
From the extracted project folder:
```powershell
python --version
g++ --version
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
g++ -std=c++17 -O2 cpp-engine\src\main.cpp -o cpp-engine\route_engine.exe
python -m uvicorn backend.main:app --reload
```
Open http://127.0.0.1:8000

If PowerShell blocks virtual-environment activation, run the venv's Python directly:
```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

## Run on Linux/macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
g++ -std=c++17 -O2 cpp-engine/src/main.cpp -o cpp-engine/route_engine
python3 -m uvicorn backend.main:app --reload
```
Open http://127.0.0.1:8000

## Use it
Choose source and destination from the dropdowns or click the map twice to select the nearest demo nodes. Choose Dijkstra or A*, then click **Find route**. The blue line shows the route through graph nodes. Use Reset to clear the route.

## Important limitations
- The sample graph is illustrative, **not an authoritative road network**. Do not use it for real navigation.
- OpenStreetMap tiles are only the visual map background; they do not provide the road graph.
- Real road navigation requires importing a regional OpenStreetMap extract, parsing road connectivity and one-way restrictions, and snapping coordinates to routable road segments.
- Tiny graph execution times are noisy; compare node counts and use repeated experiments for meaningful benchmarks.
- OpenStreetMap attribution and tile usage policy apply: https://operations.osmfoundation.org/policies/tiles/

## DAA concepts
- Adjacency-list graph representation
- Dijkstra's greedy shortest-path algorithm
- A* heuristic search using Haversine distance
- Edge relaxation and predecessor-based path reconstruction
- Complexity: heap-based Dijkstra is typically `O((V + E) log V)`.
- Empirical metrics: explored nodes and measured C++ engine time.

## API
- `GET /api/health`
- `GET /api/graph`
- `POST /api/route` with JSON `{"source":0,"target":5,"algorithm":"dijkstra"}`
- `GET /docs` for interactive API documentation.

## Structure
```text
minimap-daa/
├── backend/
├── cpp-engine/
├── frontend/
├── tests/
└── README.md
```


## Campus data accuracy

The graph uses locations inspired by the supplied conceptual campus diagram (Gate 3, S.R. Block 1, Sports Ground, J.C. Bose Block, Homi J. Bhabha Block, Central Concourse, Auditorium, Dining Complex, and hostel destinations). Coordinates and edge weights are illustrative and are **not verified building coordinates or official pedestrian routes**. Confirm facility names, locations, and paths using an official SRM AP campus map before presenting this as a real navigation system. A* uses straight-line distance as its heuristic; demo edge weights are set above the straight-line distance between connected nodes.
