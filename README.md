# AstraNav --- Graph-Based Campus Navigation

AstraNav is a graph-based campus navigation application developed to
demonstrate and compare shortest-path algorithms. It combines a **C++17
algorithm engine**, a **Python FastAPI backend**, and an interactive
**HTML/CSS/JavaScript frontend**.

Campus locations are represented as graph vertices and connections as
weighted edges. Users can select a source and destination, calculate a
route, and compare the behavior of Dijkstra's algorithm and
Bidirectional Dijkstra.

> **Research note:** The supplied graph is a schematic model. Its edge
> weights are illustrative kilometres, not independently surveyed
> pedestrian distances. Algorithmic correctness on this graph does not
> establish the accuracy of real-world campus routes.

## Features

-   Interactive campus map with source and destination selection.
-   Shortest-path calculation using Dijkstra's algorithm and
    Bidirectional Dijkstra.
-   SVG-based route visualization over the campus map.
-   Comparison of explored vertices and execution time.
-   C++17 shortest-path engine integrated with a FastAPI backend.
-   Centralized graph data stored in JSON.
-   REST API endpoints for graph retrieval, health checks, and route
    calculation.

## Technology Stack

  Layer              Technology
  ------------------ -----------------------
  Frontend           HTML, CSS, JavaScript
  Backend            Python, FastAPI
  Algorithm engine   C++17
  Graph storage      JSON
  Route overlay      SVG
  ASGI server        Uvicorn

## Algorithms

### Dijkstra's Algorithm

Dijkstra's algorithm computes minimum-cost paths from a source vertex in
a weighted graph with non-negative edge weights. AstraNav uses an
adjacency-list representation and a min-priority queue.

High-level process:

1.  Set the source distance to zero and all other distances to infinity.
2.  Extract the vertex with the smallest tentative distance.
3.  Relax its outgoing edges.
4.  Update distance and parent information when a shorter path is found.
5.  Reconstruct the route using the parent information.

With an adjacency list and binary heap, the expected time complexity is:

$$
O((|V|+|E|)\log |V|)
$$

### Bidirectional Dijkstra

Bidirectional Dijkstra performs two coordinated searches:

-   A forward search from the source.
-   A backward search from the destination, using reverse adjacency.

The implementation maintains separate distance information,
parent/successor information, settled sets, and priority queues for the
two directions. It expands the frontier with the smaller minimum
tentative distance, updates the best known connecting path, and stops
when the sum of the minimum tentative distances is no smaller than the
best known path cost.

Its worst-case asymptotic time complexity with binary heaps remains:

$$
O((|V|+|E|)\log |V|)
$$

Bidirectional search can reduce the number of explored vertices, but it
does not guarantee lower execution time for every graph or query.

## Architecture

``` text
User
 |
 v
Frontend (HTML / CSS / JavaScript)
 |
 | HTTP request
 v
FastAPI backend
 |
 | Validate request / access graph
 v
JSON graph
 |
 v
C++17 algorithm engine
 |                     |
 v                     v
Dijkstra       Bidirectional Dijkstra
 |                     |
 +----------+----------+
            |
            v
      Route and metrics
            |
            v
      FastAPI response
            |
            v
      SVG map visualization
```

## Project Structure

``` text
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
│   ├── TEST_REPORT.md
│   └── benchmarks/
│       ├── astranav_benchmark.py
│       ├── plot_benchmark.py
│       ├── benchmark_raw.csv
│       ├── benchmark_summary.csv
│       └── benchmark_comparison.csv
│
├── docs/
│   └── screenshots/
│       ├── benchmark_execution.png
│       └── algorithm_comparison.png
│
├── paper/
│   ├── main.tex
│   ├── references.bib
│   └── AstraNav.pdf
│
├── .gitignore
└── README.md
```

The `benchmarks/`, `docs/`, and `paper/` files shown above should be
included when present in your local repository. The C++ executable is
generated during setup and should not be committed as a
platform-specific binary.

## Prerequisites

Install the following:

-   Python 3.10 or later
-   A C++17-compatible compiler such as `g++`
-   `pip`
-   Node.js (only if you want to run the JavaScript syntax check)
-   Git (optional)

## Installation and Setup

Run commands from the AstraNav project root.

### Windows (PowerShell)

Create and activate a virtual environment:

``` powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install backend dependencies:

``` powershell
pip install -r backend\requirements.txt
```

Compile the C++ engine:

``` powershell
g++ -std=c++17 -O2 -Wall -Wextra -pedantic cpp-engine\src\main.cpp -o cpp-engine\route_engine.exe
```

Start the FastAPI server:

``` powershell
python -m uvicorn backend.main:app --reload
```

### Linux / macOS

Create and activate a virtual environment:

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

Install backend dependencies:

``` bash
pip install -r backend/requirements.txt
```

Compile the C++ engine:

``` bash
g++ -std=c++17 -O2 -Wall -Wextra -pedantic cpp-engine/src/main.cpp -o cpp-engine/route_engine
```

Start the FastAPI server:

``` bash
python3 -m uvicorn backend.main:app --reload
```

## Access the Application

When the server is running locally:

-   Application: <http://127.0.0.1:8000>
-   FastAPI Swagger documentation: <http://127.0.0.1:8000/docs>

The backend serves the frontend, so a separate frontend development
server is not required for the documented setup.

## API Endpoints

  Method   Endpoint        Purpose
  -------- --------------- ---------------------------------------
  GET      `/`             Serves the frontend
  GET      `/api/health`   Checks backend/engine health
  GET      `/api/graph`    Returns campus graph data
  POST     `/api/route`    Calculates a shortest path
  GET      `/docs`         FastAPI interactive API documentation

## Graph Representation

AstraNav models the campus as a weighted graph:

\[ G=(V,E) \]

-   (V): campus locations represented as vertices.
-   (E): connections represented as edges.
-   (w(u,v)): weight assigned to a connection.

The graph is stored in `cpp-engine/data/graph.json`.

### Supplied graph statistics

  Property                                Value
  ------------------- -------------------------
  Vertices                                   36
  JSON edge records                          39
  Representation                 Weighted graph
  Storage                                  JSON
  Edge weights          Illustrative kilometres

The `bidirectional` property in the graph data determines whether a
connection is traversable in both directions. The JSON file is the
source of truth for graph connectivity.

## Benchmarking and Validation

The benchmark compares Dijkstra and Bidirectional Dijkstra over all
ordered pairs of distinct vertices in the supplied graph:

\[ Q=\|V\|(\|V\|-1)=36`\times35`{=tex}=1,260 \]

The recorded final benchmark used 10 trials per pair and 10,000
in-process timing repetitions per measurement.

### Final benchmark results

  -----------------------------------------------------------------------
  Metric                               Dijkstra    Bidirectional Dijkstra
  ------------------- ------------------------- -------------------------
  Queries                                 1,260                     1,260

  Mean explored                       19.000000                 13.593651
  vertices                                      

  Mean execution time            0.001211387294            0.001577019508
  (ms)                                          

  Execution-time                 0.000378177927            0.000426942346
  standard deviation                            
  (ms)                                          

  Path validity                            100%                      100%
  -----------------------------------------------------------------------

Correctness comparison:

  Check                                     Result
  --------------------------------------- --------
  Reachability mismatches                        0
  Shortest-cost mismatches                       0
  Invalid returned paths                         0
  Unreachable queries in supplied graph          0

On this graph, Bidirectional Dijkstra explored approximately 28.45%
fewer vertices on average, while its measured mean execution time was
approximately 30.18% higher than Dijkstra's. This illustrates that
exploring fewer vertices does not necessarily result in lower execution
time; the overhead of coordinating two searches can matter, particularly
on a small graph.

The reported timing measures the repeated in-process algorithm execution
after graph loading. It excludes graph parsing, process startup, Python
orchestration, API handling, and frontend rendering. The measurements
are machine- and build-specific and should not be interpreted as
end-to-end application latency.

For methodology, detailed validation results, and limitations, see
[`tests/TEST_REPORT.md`](tests/TEST_REPORT.md).

### Run the benchmark

From the project root:

``` powershell
python tests/benchmarks/astranav_benchmark.py
```

### Generate the comparison chart

Install plotting dependencies if needed:

``` powershell
pip install pandas matplotlib
```

Then run:

``` powershell
python tests/benchmarks/plot_benchmark.py
```

The plotting script should save the chart to
`docs/screenshots/algorithm_comparison.png`. Ensure the script's input
CSV path and output path match your repository layout.

## Testing

The supplied validation run recorded:

-   Successful C++17 compilation using
    `g++ -std=c++17 -O2 -Wall -Wextra -pedantic`.
-   Successful JavaScript syntax check using `node --check`.
-   Successful Python backend compilation check.
-   HTTP 200 responses from FastAPI TestClient checks for `/`,
    `/static/app.js`, `/static/campus-map.png`, `/api/graph`, and
    `/api/health`.
-   Matching sample route cost from Gate 3 (node 0) to J.C. Bose Block
    (node 3): 0.686 illustrative kilometres.

These are results from the validated project snapshot; rerun the checks
after modifying source files.

## DAA Concepts Demonstrated

-   Graph representation and adjacency lists
-   Weighted graph traversal
-   Greedy algorithm design
-   Dijkstra's shortest-path algorithm
-   Bidirectional search
-   Priority queues and edge relaxation
-   Path reconstruction
-   Time and space complexity
-   Empirical algorithm comparison

## Limitations

-   The graph contains 36 vertices and 39 JSON edge records; performance
    results from this small graph do not establish performance on larger
    networks.
-   Edge weights are illustrative and are not independently surveyed
    walking distances.
-   The supplied graph may not contain every real campus pedestrian
    connection.
-   The campus map is a visual background; route calculation is based on
    the JSON graph.
-   Node coordinates and route overlay alignment should be visually
    checked in the browser.
-   Execution times are very small and sensitive to hardware, compiler,
    optimization flags, and measurement conditions.
-   Bidirectional Dijkstra does not guarantee fewer explored vertices or
    lower execution time for every query.

## Future Work

-   Verify graph edges against actual pedestrian walkways.
-   Survey or otherwise validate real walking distances.
-   Expand the graph to cover additional campus locations.
-   Evaluate the algorithms on larger and more varied graphs.
-   Record the exact CPU, operating system, compiler version, and build
    environment for reproducible timing studies.
-   Explore accessibility-aware routing and obstacle-aware path
    planning.

------------------------------------------------------------------------

**AstraNav --- Exploring campus routes through graph algorithms.**
