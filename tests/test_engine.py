from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"

def test_graph_shape():
    r = client.get("/api/graph")
    assert r.status_code == 200
    data = r.json()
    assert len(data["nodes"]) >= 2 and len(data["edges"]) >= 1

def test_invalid_node_rejected():
    r = client.post("/api/route", json={"source":999,"target":0,"algorithm":"dijkstra"})
    assert r.status_code == 422

def test_same_source_target():
    r = client.post("/api/route", json={"source":0,"target":0,"algorithm":"dijkstra"})
    assert r.status_code == 200
    assert r.json()["distance_km"] == 0.0
    assert r.json()["path"] == [0]
