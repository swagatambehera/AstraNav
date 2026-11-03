# AstraNav validation report

Validation performed against the supplied `graph(3).json`, `main(2).cpp`, `main(3).py`, `app(2).js`, `index.html`, `style(1).css`, and the latest supplied campus map.

## Results
- C++17 engine compiled successfully with `g++ -std=c++17 -O2 -Wall -Wextra -pedantic`.
- JavaScript syntax check passed with `node --check`.
- Python backend compiled successfully.
- FastAPI TestClient: `/`, `/static/app.js`, `/static/campus-map.png`, `/api/graph`, `/api/health` returned HTTP 200.
- Both route API algorithms returned the same sample route and distance for Gate 3 (node 0) to J.C. Bose Block (node 3): 0.686 illustrative km.
- Exhaustive comparison across all 36 x 35 = 1,260 ordered distinct source/target pairs: zero reachability or distance mismatches between Dijkstra and Bidirectional Dijkstra. All 1,260 pairs were reachable in this supplied graph.

## Important limitations
- The supplied graph has 36 nodes and 39 edges. This work corrects the application integration and keeps that graph as the sole source of truth; it does not independently redraw or certify every edge in the campus map.
- Graph weights are labelled illustrative kilometres in the supplied JSON. They are not surveyed real walking distances.
- The graph uses a 1400 x 1800 coordinate system. The supplied image is 1106 x 1422; their aspect ratios are sufficiently close for the current SVG overlay scaling, but check route alignment visually in the browser.
- The C++ executable is intentionally not bundled because Windows and Linux executables are not interchangeable. Compile it using the Windows command in README.md.
