import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH = json.loads((ROOT / "cpp-engine" / "data" / "graph.json").read_text(encoding="utf-8"))

def test_node_ids_are_contiguous():
    ids = [node["id"] for node in GRAPH["nodes"]]
    assert sorted(ids) == list(range(len(ids)))

def test_all_edges_reference_existing_nodes_and_have_nonnegative_weights():
    ids = set(node["id"] for node in GRAPH["nodes"])
    for edge in GRAPH["edges"]:
        assert edge["from"] in ids
        assert edge["to"] in ids
        assert edge["from"] != edge["to"]
        assert edge["weight"] >= 0
