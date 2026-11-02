
import json
import os
import subprocess
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

GRAPH_FILE = ROOT / "cpp-engine" / "data" / "graph.json"
FRONTEND = ROOT / "frontend"

ENGINE = ROOT / "cpp-engine" / (
    "route_engine.exe" if os.name == "nt" else "route_engine"
)


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="AstraNav - DAA Route Explorer",
    version="1.0.0",
    description=(
        "Educational campus shortest-path visualizer "
        "using C++ Dijkstra and Bidirectional Dijkstra."
    )
)


# --------------------------------------------------
# CORS CONFIGURATION
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# --------------------------------------------------
# STATIC FILES
# --------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory=str(FRONTEND)),
    name="static"
)


# --------------------------------------------------
# REQUEST MODEL
# --------------------------------------------------

class RouteRequest(BaseModel):
    source: int = Field(ge=0)
    target: int = Field(ge=0)

    algorithm: Literal[
        "dijkstra",
        "bidirectional_dijkstra"
    ] = "dijkstra"


# --------------------------------------------------
# GRAPH LOADER
# --------------------------------------------------

def load_graph():
    if not GRAPH_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Graph file not found: {GRAPH_FILE}"
        )

    try:
        with GRAPH_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Graph JSON file contains invalid JSON."
        )


# --------------------------------------------------
# HOME ROUTE
# --------------------------------------------------

@app.get("/")
def home():
    return FileResponse(FRONTEND / "index.html")


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "engine_compiled": ENGINE.exists()
    }


# --------------------------------------------------
# GRAPH API
# --------------------------------------------------

@app.get("/api/graph")
def graph():
    return load_graph()


# --------------------------------------------------
# SHORTEST PATH API
# --------------------------------------------------

@app.post("/api/route")
def route(req: RouteRequest):

    data = load_graph()

    nodes = data["nodes"]
    edges = data["edges"]

    # Validate source and destination

    if req.source >= len(nodes) or req.target >= len(nodes):
        raise HTTPException(
            status_code=422,
            detail="Source or target node ID does not exist."
        )

    # Convert graph edges into directed edges

    directed = []

    for edge in edges:

        u = edge["from"]
        v = edge["to"]
        weight = float(edge["weight"])

        directed.append((u, v, weight))

        if edge.get("bidirectional", False):
            directed.append((v, u, weight))

    # Handle identical source and destination

    if req.source == req.target:

        return {
            "found": True,
            "distance_km": 0.0,
            "path": [req.source],
            "explored_nodes": 1,
            "execution_ms": 0.0,
            "algorithm": req.algorithm,
            "nodes": [nodes[req.source]]
        }

    # Check C++ executable

    if not ENGINE.exists():
        raise HTTPException(
            status_code=500,
            detail=(
                "C++ engine is not compiled. "
                "Check the executable path and build instructions."
            )
        )

    # Prepare input for C++ engine

    lines = [
        f"{len(nodes)} {len(directed)} "
        f"{req.source} {req.target} {req.algorithm}"
    ]

    lines.extend(
        f'{node["id"]} {node["lat"]} {node["lon"]}'
        for node in nodes
    )

    lines.extend(
        f"{u} {v} {weight}"
        for u, v, weight in directed
    )

    engine_input = "\n".join(lines) + "\n"

    # Execute C++ shortest-path engine

    try:

        completed = subprocess.run(
            [str(ENGINE)],
            input=engine_input,
            text=True,
            capture_output=True,
            timeout=5,
            check=False
        )

    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=504,
            detail="Route calculation timed out."
        )

    # Check C++ execution status

    if completed.returncode != 0:

        raise HTTPException(
            status_code=500,
            detail="C++ engine failed: " + completed.stderr[:300]
        )

    # Parse C++ JSON output

    try:

        result = json.loads(completed.stdout)

    except json.JSONDecodeError:

        raise HTTPException(
            status_code=500,
            detail="C++ engine returned invalid JSON."
        )

    # Add algorithm information

    result["algorithm"] = req.algorithm

    # Convert returned path IDs into complete node objects

    try:
        result["nodes"] = [
            nodes[node_id]
            for node_id in result["path"]
        ]

    except (IndexError, TypeError, KeyError):
        raise HTTPException(
            status_code=500,
            detail="C++ engine returned an invalid node path."
        )

    return result
