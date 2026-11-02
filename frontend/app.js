const IMAGE_WIDTH = 1055;
const IMAGE_HEIGHT = 1414;
const API_BASE = "http://127.0.0.1:8000";

const map = L.map("map", {
  crs: L.CRS.Simple,
  minZoom: -1.5,
  maxZoom: 2,
  zoomSnap: 0.25,
  zoomDelta: 0.25,
  maxBoundsViscosity: 1
});

const imageBounds = [[0, 0], [IMAGE_HEIGHT, IMAGE_WIDTH]];

// campus-map.png is in the same folder as index.html and app.js.
L.imageOverlay("./campus-map.png", imageBounds).addTo(map);
map.fitBounds(imageBounds);
map.setMaxBounds([[-40, -40], [IMAGE_HEIGHT + 40, IMAGE_WIDTH + 40]]);

let graph = null;
let routeLayer = null;
let edgeLayer = null;
let markers = [];
let selectedAlgorithm = "dijkstra";
let clickCount = 0;

const sourceSelect = document.getElementById("source");
const targetSelect = document.getElementById("target");
const errorBox = document.getElementById("error");

function clearRoute() {
  if (routeLayer) map.removeLayer(routeLayer);
  routeLayer = null;

  ["distance", "resultAlgorithm", "explored", "runtime", "pathLength"]
    .forEach(id => {
      document.getElementById(id).textContent = "—";
    });

  document.getElementById("pathList").innerHTML =
    '<li class="muted">Calculate a route to see the path.</li>';
  errorBox.textContent = "";
}

function nodeById(id) {
  return graph.nodes.find(node => node.id === Number(id));
}

function nearestNode(latlng) {
  let best = graph.nodes[0];
  let bestDistance = Infinity;

  for (const node of graph.nodes) {
    const dLat = latlng.lat - (IMAGE_HEIGHT - node.y);
    const dLon = latlng.lng - node.x;
    const distance = dLat * dLat + dLon * dLon;

    if (distance < bestDistance) {
      bestDistance = distance;
      best = node;
    }
  }

  return best;
}

function imageLatLng(node) {
  return [IMAGE_HEIGHT - node.y, node.x];
}

function renderGraph() {
  if (edgeLayer) map.removeLayer(edgeLayer);
  markers.forEach(marker => map.removeLayer(marker));
  markers = [];

  const edgeLines = graph.edges.map(edge => {
    const from = nodeById(edge.from);
    const to = nodeById(edge.to);

    if (!from || !to) return null;

    return L.polyline([imageLatLng(from), imageLatLng(to)], {
      color: "#9ca3af",
      weight: 2.5,
      opacity: 0.8,
      dashArray: "5 6"
    }).bindTooltip(`${Number(edge.weight).toFixed(2)} km (illustrative edge)`);
  }).filter(Boolean);

  edgeLayer = L.featureGroup(edgeLines).addTo(map);

  for (const node of graph.nodes) {
    const marker = L.circleMarker(imageLatLng(node), {
      radius: 6,
      color: "#14532d",
      weight: 2,
      fillColor: "#4ade80",
      fillOpacity: 1
    }).addTo(map).bindTooltip(`${node.name} · Node ${node.id}`);

    markers.push(marker);
  }
}

function populate() {
  for (const select of [sourceSelect, targetSelect]) {
    select.innerHTML = "";

    graph.nodes.forEach(node => {
      const option = document.createElement("option");
      option.value = node.id;
      option.textContent = node.name;
      select.appendChild(option);
    });
  }

  // Preserve the original defaults when those node IDs exist.
  sourceSelect.value = nodeById(15) ? "15" : String(graph.nodes[0]?.id ?? "");
  targetSelect.value = nodeById(10)
    ? "10"
    : String(graph.nodes[1]?.id ?? graph.nodes[0]?.id ?? "");
}

async function loadGraph() {
  const response = await fetch(`${API_BASE}/api/graph`);

  if (!response.ok) {
    throw new Error(`Could not load graph (${response.status}). Check the backend.`);
  }

  graph = await response.json();

  if (!graph || !Array.isArray(graph.nodes) || !Array.isArray(graph.edges)) {
    throw new Error("Backend returned an invalid graph. Expected nodes and edges arrays.");
  }

  if (!graph.nodes.every(node =>
    Number.isFinite(Number(node.x)) && Number.isFinite(Number(node.y))
  )) {
    throw new Error("Graph is missing image coordinates x/y. Check graph.json.");
  }

  populate();
  renderGraph();
  map.fitBounds(imageBounds);
}

document.querySelectorAll(".algo").forEach(button => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".algo").forEach(item => item.classList.remove("active"));
    button.classList.add("active");
    selectedAlgorithm = button.dataset.algo;
  });
});

document.getElementById("findRoute").addEventListener("click", async () => {
  clearRoute();

  const button = document.getElementById("findRoute");
  button.disabled = true;
  button.textContent = "Calculating…";

  try {
    const response = await fetch(`${API_BASE}/api/route`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        source: Number(sourceSelect.value),
        target: Number(targetSelect.value),
        algorithm: selectedAlgorithm
      })
    });

    let result;

    try {
      result = await response.json();
    } catch (_) {
      throw new Error(`Backend returned an invalid response (HTTP ${response.status}).`);
    }

    if (!response.ok) {
      throw new Error(result.detail || `Route calculation failed (HTTP ${response.status}).`);
    }

    if (!result.found || !Array.isArray(result.nodes) || result.nodes.length === 0) {
      throw new Error("No route connects these locations.");
    }

    routeLayer = L.polyline(result.nodes.map(imageLatLng), {
      color: "#15803d",
      weight: 6,
      opacity: 0.98,
      lineCap: "round",
      lineJoin: "round"
    }).addTo(map);

    map.fitBounds(routeLayer.getBounds().pad(0.18));

    document.getElementById("distance").textContent =
      Number(result.distance_km).toFixed(2);

    document.getElementById("resultAlgorithm").textContent =
      result.algorithm === "bidirectional_dijkstra"
        ? "Bidirectional Dijkstra"
        : "Dijkstra";

    document.getElementById("explored").textContent = result.explored_nodes;
    document.getElementById("runtime").textContent =
      `${Number(result.execution_ms).toFixed(3)} ms`;
    document.getElementById("pathLength").textContent = result.path.length;

    const list = document.getElementById("pathList");
    list.innerHTML = "";

    result.nodes.forEach(node => {
      const item = document.createElement("li");
      item.textContent = `${node.name} (node ${node.id})`;
      list.appendChild(item);
    });
  } catch (error) {
    errorBox.textContent =
      error instanceof TypeError
        ? "Cannot connect to the backend. Make sure FastAPI is running at http://127.0.0.1:8000."
        : error.message;
  } finally {
    button.disabled = false;
    button.innerHTML = 'Find route <span>→</span>';
  }
});

document.getElementById("reset").addEventListener("click", () => {
  clearRoute();

  if (graph) {
    renderGraph();
    map.fitBounds(imageBounds);
  }
});

map.on("click", event => {
  if (!graph || graph.nodes.length === 0) return;

  const node = nearestNode(event.latlng);

  if (clickCount % 2 === 0) {
    sourceSelect.value = String(node.id);
  } else {
    targetSelect.value = String(node.id);
  }

  clickCount++;
  clearRoute();
});

loadGraph().catch(error => {
  errorBox.textContent = error.message;
});
