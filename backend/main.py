import json
import math
import os
import subprocess
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
GRAPH_FILE = ROOT / "cpp-engine" / "data" / "graph.json"
FRONTEND = ROOT / "frontend"
ENGINE = ROOT / "cpp-engine" / ("route_engine.exe" if os.name == "nt" else "route_engine")

app = FastAPI(
    title="AstraNav - SRM AP Campus Route Explorer",
    version="2.1.0",
    description="Campus pedestrian shortest paths using C++17 Dijkstra algorithms."
)

# FastAPI serves both the frontend and API on the same origin (port 8000).
# CORS middleware is intentionally unnecessary in this deployment.
app.mount("/static", StaticFiles(directory=str(FRONTEND)), name="static")


class RouteRequest(BaseModel):
    source: int = Field(ge=0)
    target: int = Field(ge=0)
    algorithm: Literal["dijkstra", "bidirectional_dijkstra"] = "dijkstra"


def load_graph():
    try:
        data = json.loads(GRAPH_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Campus graph file is missing.")
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f"Campus graph JSON is invalid: {exc}")

    nodes, edges = data.get("nodes"), data.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list) or not nodes:
        raise HTTPException(status_code=500, detail="Graph must contain non-empty nodes and an edges list.")

    ids = [node.get("id") for node in nodes]
    if sorted(ids) != list(range(len(nodes))):
        raise HTTPException(status_code=500, detail="Node IDs must be contiguous from 0 to N-1.")

    for edge in edges:
        if not isinstance(edge, dict):
            raise HTTPException(status_code=500, detail="Each graph edge must be an object.")
        u, v, weight = edge.get("from"), edge.get("to"), edge.get("weight")
        if (not isinstance(u, int) or isinstance(u, bool) or
            not isinstance(v, int) or isinstance(v, bool) or
            u not in ids or v not in ids or u == v):
            raise HTTPException(status_code=500, detail="Graph contains an invalid edge endpoint.")
        if (not isinstance(weight, (int, float)) or isinstance(weight, bool)
            or not math.isfinite(weight) or weight < 0):
            raise HTTPException(status_code=500, detail="Edge weights must be finite, non-negative numbers.")
    return data


@app.get("/")
def home():
    return FileResponse(FRONTEND / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "engine_compiled": ENGINE.exists()}


@app.get("/api/graph")
def graph():
    return load_graph()


@app.post("/api/route")
def route(req: RouteRequest):
    data = load_graph()
    nodes, edges = data["nodes"], data["edges"]

    if req.source >= len(nodes) or req.target >= len(nodes):
        raise HTTPException(status_code=422, detail="Source or destination node does not exist.")

    if req.source == req.target:
        return {
            "found": True, "distance_km": 0.0, "path": [req.source],
            "explored_nodes": 1, "execution_ms": 0.0,
            "algorithm": req.algorithm, "nodes": [nodes[req.source]]
        }

    if not ENGINE.is_file():
        raise HTTPException(status_code=500, detail="C++ engine is not compiled. Follow the build command in README.md.")

    directed = []
    allowed = set()
    for edge in edges:
        u, v, weight = edge["from"], edge["to"], float(edge["weight"])
        directed.append((u, v, weight))
        allowed.add((u, v))
        if edge.get("bidirectional", False):
            directed.append((v, u, weight))
            allowed.add((v, u))

    lines = [f"{len(nodes)} {len(directed)} {req.source} {req.target} {req.algorithm}"]
    lines.extend(f'{node["id"]} {float(node.get("lat", 0))} {float(node.get("lon", 0))}' for node in nodes)
    lines.extend(f"{u} {v} {weight:.10f}" for u, v, weight in directed)

    try:
        completed = subprocess.run(
            [str(ENGINE)], input="\n".join(lines) + "\n",
            text=True, capture_output=True, timeout=5, check=False
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Route calculation timed out.")
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"Could not start C++ engine: {exc}")

    if completed.returncode != 0:
        raise HTTPException(status_code=500, detail=f"C++ engine failed: {completed.stderr[:500]}")

    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="C++ engine returned invalid JSON.")

    path = result.get("path", [])
    if result.get("found"):
        if not isinstance(path, list) or not path or path[0] != req.source or path[-1] != req.target:
            raise HTTPException(status_code=500, detail="Engine returned an invalid route.")
        if any(not isinstance(i, int) or i < 0 or i >= len(nodes) for i in path):
            raise HTTPException(status_code=500, detail="Engine returned an unknown node ID.")
        if any((a, b) not in allowed for a, b in zip(path, path[1:])):
            raise HTTPException(status_code=500, detail="Engine route contains a non-existent walkway edge.")

    result["algorithm"] = req.algorithm
    result["nodes"] = [nodes[i] for i in path] if result.get("found") else []
    return result
