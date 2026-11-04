# AstraNav --- Benchmark and Validation Report

## 1. Purpose

This report documents the correctness validation and performance
comparison of the two shortest-path algorithms implemented in AstraNav:

-   Dijkstra's algorithm
-   Bidirectional Dijkstra's algorithm

The experiments use the campus graph supplied with the project. The
report distinguishes algorithmic correctness on this graph from the
accuracy of the graph as a representation of real campus walking routes.

## 2. Experimental Setup

  Item                                                              Value
  ------------------------------------ ----------------------------------
  Graph vertices                                                       36
  JSON edge records                                                    39
  Ordered source--destination pairs                                 1,260
  Trials per pair, per algorithm                                       10
  Timing repetitions per measurement                               10,000
  Total raw timing observations                                    25,200
  Algorithms compared                    Dijkstra, Bidirectional Dijkstra

The number of ordered distinct source--destination pairs is:

\[ Q = \|V\|(\|V\|-1) = 36 `\times 35`{=tex} = 1,260 \]

Each algorithm was evaluated for every ordered pair of distinct
vertices. Each pair/algorithm combination had 10 trials. Each timing
observation measured 10,000 in-process executions and reported the
average duration per execution.

The graph is stored in `cpp-engine/data/graph.json`. The benchmark uses
the graph and algorithm implementation supplied with AstraNav.

### Timing scope

The C++ engine loads/parses the graph before starting the repeated
algorithm timing loop. The reported algorithm time therefore excludes
graph parsing. The benchmark invokes the executable as a separate
process for measurements, so process startup, Python orchestration,
FastAPI/API handling, and frontend rendering are not included in the
reported per-execution algorithm time.

The timing values are extremely small and are specific to the tested
machine, compiler, build, and graph. They should not be interpreted as
end-to-end application latency or generalized performance guarantees.

## 3. Correctness Validation

Both algorithms were compared across all 1,260 ordered
source--destination pairs in the supplied graph.

  Validation metric                               Dijkstra   Bidirectional Dijkstra
  --------------------------------------------- ---------- ------------------------
  Queries evaluated                                  1,260                    1,260
  Path validity                                       100%                     100%
  Unreachable queries                                    0                        0
  Invalid returned paths                                 0                        0
  Reachability mismatches between algorithms             0                        0
  Shortest-cost mismatches between algorithms            0                        0

No reachability or shortest-cost mismatches were observed in this
exhaustive all-pairs comparison on the supplied graph. All 1,260
source--destination pairs were reachable in this graph.

This is an experimental validation for the supplied graph and
implementation. It is not, by itself, a formal proof of correctness for
all possible graphs.

## 4. Performance Results

### 4.1 Aggregate measurements

  -----------------------------------------------------------------------
  Metric                               Dijkstra    Bidirectional Dijkstra
  ------------------- ------------------------- -------------------------
  Queries                                 1,260                     1,260

  Trials per query                           10                        10

  Timing repetitions                     10,000                    10,000
  per measurement                               

  Mean explored                       19.000000                 13.593651
  vertices                                      

  Mean execution time            0.001211387294            0.001577019508
  (ms)                                          

  Execution-time                 0.000378177927            0.000426942346
  standard deviation                            
  (ms)                                          

  Path validity                            100%                      100%

  Unreachable queries                         0                         0
  -----------------------------------------------------------------------

### 4.2 Interpretation

On this graph and workload, Bidirectional Dijkstra explored fewer
vertices on average:

-   Dijkstra: 19.000000 explored vertices.
-   Bidirectional Dijkstra: 13.593651 explored vertices.

This is approximately 28.45% fewer explored vertices for Bidirectional
Dijkstra, relative to Dijkstra's mean.

However, Bidirectional Dijkstra had a higher measured mean execution
time:

-   Dijkstra: 0.001211387294 ms.
-   Bidirectional Dijkstra: 0.001577019508 ms.

For this benchmark, Bidirectional Dijkstra's mean execution time was
approximately 30.18% higher than Dijkstra's, relative to Dijkstra's
mean.

These results illustrate that reducing the number of explored vertices
does not necessarily reduce wall-clock execution time. Bidirectional
search maintains and coordinates two search frontiers and associated
state, which can introduce overhead. On a small graph, that overhead can
outweigh the benefit of exploring fewer vertices.

The result is specific to this graph, implementation, build, and test
environment. It should not be generalized to larger or structurally
different networks without further experiments.

## 5. Implementation and Build Validation

The following checks were recorded for the supplied project version:

  ----------------------------------------------------------------------------------
  Check                                          Result
  ---------------------------------------------- -----------------------------------
  C++17 compilation using                        Passed
  `g++ -std=c++17 -O2 -Wall -Wextra -pedantic`   

  JavaScript syntax check using `node --check`   Passed

  Python backend compilation check               Passed

  FastAPI TestClient checks for `/`,             HTTP 200
  `/static/app.js`, `/static/campus-map.png`,    
  `/api/graph`, `/api/health`                    

  Sample route API comparison, Gate 3 (node 0)   Same route cost from both
  to J.C. Bose Block (node 3)                    algorithms
  ----------------------------------------------------------------------------------

The sample route had a reported graph cost of 0.686 illustrative
kilometres. This is a graph weight, not a surveyed pedestrian distance.

## 6. Reproducibility

The benchmark artifacts should be kept together under:

``` text
tests/
├── TEST_REPORT.md
└── benchmarks/
    ├── astranav_benchmark.py
    ├── plot_benchmark.py
    ├── benchmark_raw.csv
    ├── benchmark_summary.csv
    └── benchmark_comparison.csv
```

Run the benchmark from the project root using the command appropriate to
the script's current arguments and environment:

``` powershell
python tests/benchmarks/astranav_benchmark.py
```

Generate the comparison chart with:

``` powershell
python tests/benchmarks/plot_benchmark.py
```

The benchmark script, CSV files, compiler version, operating system,
CPU, and exact source revision should be retained with the experiment to
support independent reproduction. The available results do not specify
the exact compiler version, operating system, or benchmark CPU; these
environment details should be added before treating the report as a
fully reproducible published experiment.

## 7. Limitations

1.  **Graph size:** The evaluation uses one graph containing 36 vertices
    and 39 JSON edge records. It does not establish performance on
    larger networks.
2.  **Illustrative weights:** The graph's edge weights are illustrative
    kilometres, not independently surveyed walking distances.
3.  **Map alignment:** The map is a visual background and the route is
    computed from the JSON graph. Visual alignment should be checked in
    the browser.
4.  **Graph completeness:** The supplied graph may not include every
    real-world campus pedestrian connection. Its topology and
    coordinates have not been independently certified against all campus
    walkways.
5.  **Timing sensitivity:** The measured execution times are very small
    and depend on the hardware, compiler, optimization flags, and
    measurement environment.
6.  **No universal speedup claim:** Bidirectional Dijkstra does not
    guarantee fewer explored vertices or lower execution time for every
    source--destination pair or graph.
7.  **Scope of validation:** The all-pairs comparison establishes
    agreement between the two implementations on this supplied graph; it
    does not replace formal verification or independent ground-truth
    route validation.

## 8. Conclusion

For the supplied AstraNav campus graph, Dijkstra and Bidirectional
Dijkstra returned valid paths with matching shortest costs for all 1,260
ordered source--destination pairs. No invalid paths, unreachable
queries, reachability mismatches, or shortest-cost mismatches were
observed.

Bidirectional Dijkstra explored approximately 28.45% fewer vertices on
average, but its measured mean execution time was approximately 30.18%
higher than Dijkstra's. The experiment therefore demonstrates a
trade-off between search-space reduction and implementation overhead on
this small graph, rather than a universal runtime advantage.

Future evaluation should use larger graphs, independently verified
pedestrian connections and distances, and a documented hardware/software
environment.
