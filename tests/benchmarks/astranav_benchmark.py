#!/usr/bin/env python3
"""
AstraNav benchmark runner.

Runs every ordered source-destination pair (excluding source == destination)
through the compiled C++ engine for Dijkstra and Bidirectional Dijkstra.

The engine's execution_ms is measured inside the algorithm, after graph input
has been parsed. Process launch and graph-input time are therefore excluded
from the reported algorithm execution time.
"""

import argparse
import csv
import json
import math
import os
import statistics
import subprocess
import sys
from pathlib import Path

ALGORITHMS = ("dijkstra", "bidirectional_dijkstra")
COST_TOLERANCE = 1e-8


def load_graph(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    nodes = data.get("nodes")
    edges = data.get("edges")

    if not isinstance(nodes, list) or not nodes:
        raise ValueError("Graph JSON must contain a non-empty 'nodes' list.")
    if not isinstance(edges, list):
        raise ValueError("Graph JSON must contain an 'edges' list.")

    ids = [node.get("id") for node in nodes]
    if sorted(ids) != list(range(len(nodes))):
        raise ValueError("Node IDs must be contiguous integers from 0 to N-1.")

    n = len(nodes)
    directed_edges = []
    allowed = set()
    weight_by_arc = {}

    for edge in edges:
        u, v, w = edge.get("from"), edge.get("to"), edge.get("weight")
        if not isinstance(u, int) or not isinstance(v, int):
            raise ValueError(f"Invalid edge endpoints: {edge}")
        if not (0 <= u < n and 0 <= v < n) or u == v:
            raise ValueError(f"Edge endpoint out of range or self-edge: {edge}")
        if not isinstance(w, (int, float)) or not math.isfinite(w) or w < 0:
            raise ValueError(f"Invalid edge weight: {edge}")

        directed_edges.append((u, v, float(w)))
        allowed.add((u, v))
        weight_by_arc[(u, v)] = float(w)

        if edge.get("bidirectional", False):
            directed_edges.append((v, u, float(w)))
            allowed.add((v, u))
            weight_by_arc[(v, u)] = float(w)

    return data, nodes, directed_edges, allowed, weight_by_arc


def make_engine_input(nodes, directed_edges, source, target, algorithm):
    lines = [
        f"{len(nodes)} {len(directed_edges)} {source} {target} {algorithm}"
    ]

    for node in nodes:
        node_id = node["id"]
        lat = float(node.get("lat", 0.0))
        lon = float(node.get("lon", 0.0))
        lines.append(f"{node_id} {lat:.12f} {lon:.12f}")

    for u, v, weight in directed_edges:
        lines.append(f"{u} {v} {weight:.12f}")

    return "\n".join(lines) + "\n"


def run_once(engine, payload, timing_repetitions):
    env = os.environ.copy()
    env["ASTRANAV_BENCH_REPETITIONS"] = str(timing_repetitions)
    completed = subprocess.run(
        [str(engine)],
        input=payload,
        text=True,
        capture_output=True,
        timeout=120,
        check=False,
        env=env,
    )

    if completed.returncode != 0:
        raise RuntimeError(
            f"Engine returned {completed.returncode}: {completed.stderr.strip()}"
        )

    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Engine returned invalid JSON: {completed.stdout!r}"
        ) from exc

    required = ("found", "distance_km", "explored_nodes", "execution_ms", "path")
    missing = [key for key in required if key not in result]
    if missing:
        raise RuntimeError(f"Engine output is missing fields: {missing}")

    return result


def validate_result(result, source, target, allowed, weight_by_arc):
    if not result["found"]:
        return False, 0.0, "unreachable"

    path = result["path"]
    if not isinstance(path, list) or not path:
        return False, 0.0, "empty path"
    if path[0] != source or path[-1] != target:
        return False, 0.0, "wrong source or destination"

    total = 0.0
    for u, v in zip(path, path[1:]):
        if (u, v) not in allowed:
            return False, 0.0, f"non-edge in path: {u}->{v}"
        total += weight_by_arc[(u, v)]

    if not math.isclose(
        total, float(result["distance_km"]),
        rel_tol=1e-8, abs_tol=COST_TOLERANCE
    ):
        return False, total, "reported distance does not equal path edge sum"

    return True, total, ""


def main():
    parser = argparse.ArgumentParser(description="Benchmark AstraNav C++ algorithms.")
    parser.add_argument(
        "--graph",
        default="cpp-engine/data/graph.json",
        help="Path to graph JSON (default: cpp-engine/data/graph.json)",
    )
    parser.add_argument(
        "--engine",
        default=None,
        help="Path to compiled engine. Defaults to route_engine.exe on Windows or route_engine elsewhere.",
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=5,
        help="Number of measured repetitions per pair and algorithm (default: 5).",
    )
    parser.add_argument(
        "--timing-repetitions",
        type=int,
        default=1000,
        help="Number of in-process algorithm repetitions per measurement (default: 1000).",
    )
    parser.add_argument(
        "--out",
        default="benchmark-results",
        help="Output directory (default: benchmark-results).",
    )
    args = parser.parse_args()

    if args.trials < 1:
        parser.error("--trials must be at least 1")
    if args.timing_repetitions < 1:
        parser.error("--timing-repetitions must be at least 1")

    root = Path.cwd()
    graph_path = (root / args.graph).resolve()
    if args.engine:
        engine_path = (root / args.engine).resolve()
    else:
        engine_name = "route_engine.exe" if sys.platform.startswith("win") else "route_engine"
        engine_path = (root / "cpp-engine" / engine_name).resolve()

    if not graph_path.is_file():
        raise SystemExit(f"Graph file not found: {graph_path}")
    if not engine_path.is_file():
        raise SystemExit(
            f"Compiled engine not found: {engine_path}\n"
            "Compile main.cpp first; see the commands in the instructions."
        )

    data, nodes, directed_edges, allowed, weight_by_arc = load_graph(graph_path)
    n = len(nodes)
    pairs = [(s, t) for s in range(n) for t in range(n) if s != t]
    expected_pairs = n * (n - 1)

    out_dir = (root / args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_path = out_dir / "benchmark_raw.csv"
    summary_path = out_dir / "benchmark_summary.csv"
    comparison_path = out_dir / "benchmark_comparison.csv"

    # Store per-query results for each algorithm across all trials.
    observations = {
        algorithm: {pair: [] for pair in pairs}
        for algorithm in ALGORITHMS
    }
    time_values = {algorithm: [] for algorithm in ALGORITHMS}
    explored_values = {algorithm: [] for algorithm in ALGORITHMS}
    invalid_records = []
    unreachable_by_algorithm = {algorithm: set() for algorithm in ALGORITHMS}

    print(f"Graph: {graph_path}")
    print(f"Vertices: {n}; original JSON edges: {len(data['edges'])}")
    print(f"Directed arcs sent to engine: {len(directed_edges)}")
    print(f"Ordered distinct source-destination pairs: {expected_pairs}")
    print(f"Algorithms: {', '.join(ALGORITHMS)}")
    print(f"Measured trials per pair/algorithm: {args.trials}")
    print(f"In-process timing repetitions per measurement: {args.timing_repetitions}")
    print(f"Total measured engine runs: {expected_pairs * 2 * args.trials}")
    print("Starting benchmark...")

    with raw_path.open("w", newline="", encoding="utf-8") as raw_file:
        writer = csv.DictWriter(
            raw_file,
            fieldnames=[
                "source_id", "source_name", "target_id", "target_name",
                "algorithm", "trial", "found", "path_cost",
                "path_valid", "explored_vertices", "execution_ms",
                "timing_repetitions",
                "path", "validation_note",
            ],
        )
        writer.writeheader()

        run_number = 0
        total_runs = expected_pairs * len(ALGORITHMS) * args.trials

        for algorithm in ALGORITHMS:
            for source, target in pairs:
                payload = make_engine_input(
                    nodes, directed_edges, source, target, algorithm
                )

                for trial in range(1, args.trials + 1):
                    run_number += 1
                    result = run_once(engine_path, payload, args.timing_repetitions)

                    valid, path_cost, note = validate_result(
                        result, source, target, allowed, weight_by_arc
                    )

                    if result["found"] and not valid:
                        invalid_records.append(
                            (algorithm, source, target, trial, note)
                        )

                    if not result["found"]:
                        unreachable_by_algorithm[algorithm].add((source, target))

                    execution_ms = float(result["execution_ms"])
                    explored = int(result["explored_nodes"])

                    time_values[algorithm].append(execution_ms)
                    explored_values[algorithm].append(explored)
                    observations[algorithm][(source, target)].append(result)

                    writer.writerow({
                        "source_id": source,
                        "source_name": nodes[source].get("name", str(source)),
                        "target_id": target,
                        "target_name": nodes[target].get("name", str(target)),
                        "algorithm": algorithm,
                        "trial": trial,
                        "found": result["found"],
                        "path_cost": result["distance_km"] if result["found"] else "",
                        "path_valid": valid if result["found"] else "",
                        "explored_vertices": explored,
                        "execution_ms": f"{execution_ms:.12f}",
                        "timing_repetitions": int(result.get("timing_repetitions", args.timing_repetitions)),
                        "path": "->".join(map(str, result["path"])),
                        "validation_note": note,
                    })

                    if run_number % 500 == 0 or run_number == total_runs:
                        print(f"Completed {run_number}/{total_runs} runs...")

    # Compare one representative cost per pair; repeated trials should be deterministic.
    mismatches = []
    pair_validity = {algorithm: 0 for algorithm in ALGORITHMS}
    pair_reachable = {algorithm: 0 for algorithm in ALGORITHMS}

    for pair in pairs:
        for algorithm in ALGORITHMS:
            runs = observations[algorithm][pair]
            if runs and runs[0]["found"]:
                pair_reachable[algorithm] += 1
                is_valid, _, _ = validate_result(
                    runs[0], pair[0], pair[1], allowed, weight_by_arc
                )
                if is_valid:
                    pair_validity[algorithm] += 1

        d = observations["dijkstra"][pair][0]
        b = observations["bidirectional_dijkstra"][pair][0]

        if d["found"] != b["found"]:
            mismatches.append((pair, "reachability mismatch"))
        elif d["found"] and not math.isclose(
            float(d["distance_km"]),
            float(b["distance_km"]),
            rel_tol=1e-8,
            abs_tol=COST_TOLERANCE,
        ):
            mismatches.append((pair, "shortest-path cost mismatch"))

    summary_rows = []
    for algorithm in ALGORITHMS:
        validity_pct = (100.0 * pair_validity[algorithm] / pair_reachable[algorithm]) if pair_reachable[algorithm] else 100.0
        mean_explored = statistics.mean(explored_values[algorithm])
        mean_time = statistics.mean(time_values[algorithm])
        stdev_time = (
            statistics.stdev(time_values[algorithm])
            if len(time_values[algorithm]) > 1 else 0.0
        )

        summary_rows.append({
            "algorithm": algorithm,
            "queries_completed": expected_pairs,
            "path_validity_percent": f"{validity_pct:.4f}",
            "path_valid_pairs": pair_validity[algorithm],
            "path_cost_mismatches_vs_dijkstra": (
                "0" if algorithm == "dijkstra" else str(
                    sum(1 for _, reason in mismatches if "cost" in reason or "reachability" in reason)
                )
            ),
            "mean_explored_vertices": f"{mean_explored:.6f}",
            "mean_execution_time_ms": f"{mean_time:.12f}",
            "execution_time_stdev_ms": f"{stdev_time:.12f}",
            "timing_repetitions_per_measurement": args.timing_repetitions,
            "unreachable_queries": len(unreachable_by_algorithm[algorithm]),
        })

    with summary_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)

    with comparison_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source_id", "target_id", "dijkstra_cost",
                         "bidirectional_cost", "cost_match"])
        for source, target in pairs:
            d = observations["dijkstra"][(source, target)][0]
            b = observations["bidirectional_dijkstra"][(source, target)][0]
            match = (
                d["found"] == b["found"]
                and (
                    not d["found"]
                    or math.isclose(
                        float(d["distance_km"]),
                        float(b["distance_km"]),
                        rel_tol=1e-8,
                        abs_tol=COST_TOLERANCE,
                    )
                )
            )
            writer.writerow([
                source, target,
                d["distance_km"] if d["found"] else "",
                b["distance_km"] if b["found"] else "",
                match,
            ])

    print("\n=== BENCHMARK SUMMARY ===")
    for row in summary_rows:
        print(
            f"{row['algorithm']}: "
            f"queries={row['queries_completed']}, "
            f"path validity={row['path_validity_percent']}%, "
            f"mean explored={row['mean_explored_vertices']}, "
            f"mean time={row['mean_execution_time_ms']} ms, "
            f"time SD={row['execution_time_stdev_ms']} ms, "
            f"unreachable={row['unreachable_queries']}"
        )

    print(f"\nReachability/shortest-cost mismatches: {len(mismatches)}")
    print(f"Invalid returned paths: {len(invalid_records)}")
    print("\nFiles written:")
    print(f"  {raw_path}")
    print(f"  {summary_path}")
    print(f"  {comparison_path}")

    if mismatches or invalid_records:
        print("\nWARNING: Do not report this benchmark as passing.")
        print("Investigate graph consistency, path validation, and the")
        print("Bidirectional Dijkstra termination/reconstruction logic.")
        return 2

    print("\nPASS: Both algorithms agreed on reachability and shortest-path cost,")
    print("and all returned paths passed edge/path-cost validation.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, KeyError, TypeError) as exc:
        print(f"BENCHMARK ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
