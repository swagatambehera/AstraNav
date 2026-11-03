const sourceEl = document.querySelector("#source");
const targetEl = document.querySelector("#target");
const algorithmEl = document.querySelector("#algorithm");
const findButton = document.querySelector("#find");
const resetButton = document.querySelector("#reset");
const svg = document.querySelector("#overlay");
const statusEl = document.querySelector("#status");
const resultEl = document.querySelector("#result");

let campusGraph = null;
let isBusy = false;

async function loadCampusGraph() {
  try {
    const response = await fetch("/api/graph");
    if (!response.ok) throw new Error(`Graph API returned HTTP ${response.status}`);
    campusGraph = await response.json();

    const destinations = campusGraph.nodes.filter(
      node => node.category !== "Junction" && !/junction/i.test(node.name)
    );

    for (const node of destinations) {
      for (const select of [sourceEl, targetEl]) {
        const option = document.createElement("option");
        option.value = String(node.id);
        option.textContent = node.name;
        select.appendChild(option);
      }
    }

    // Sensible initial selection: Gate 3 -> J.C. Bose Block.
    sourceEl.value = "0";
    targetEl.value = "3";
    sourceEl.disabled = false;
    targetEl.disabled = false;
    findButton.disabled = false;
    statusEl.textContent = `Campus graph loaded: ${campusGraph.nodes.length} nodes and ${campusGraph.edges.length} walkway links.`;
  } catch (error) {
    statusEl.textContent = `Could not load campus graph: ${error.message}`;
  }
}

function clearRoute() {
  svg.replaceChildren();
}

function drawRoute(pathNodes) {
  clearRoute();
  if (!pathNodes || pathNodes.length === 0) return;

  // The SVG viewBox uses the graph's original coordinate system (1400 x 1800).
  const points = pathNodes.map(node => `${node.x},${node.y}`).join(" ");
  const ns = "http://www.w3.org/2000/svg";

  const outline = document.createElementNS(ns, "polyline");
  outline.setAttribute("points", points);
  outline.setAttribute("class", "route-under");
  svg.appendChild(outline);

  const route = document.createElementNS(ns, "polyline");
  route.setAttribute("points", points);
  route.setAttribute("class", "route");
  svg.appendChild(route);

  const addMarker = (node, className, label) => {
    const group = document.createElementNS(ns, "g");
    const circle = document.createElementNS(ns, "circle");
    circle.setAttribute("cx", node.x);
    circle.setAttribute("cy", node.y);
    circle.setAttribute("r", "15");
    circle.setAttribute("class", className);
    const title = document.createElementNS(ns, "title");
    title.textContent = `${label}: ${node.name}`;
    circle.appendChild(title);
    group.appendChild(circle);
    svg.appendChild(group);
  };

  addMarker(pathNodes[0], "pin-start", "Start");
  if (pathNodes.length > 1) addMarker(pathNodes[pathNodes.length - 1], "pin-end", "Destination");
}

function formatDistance(km) {
  if (km < 1) return `${(km * 1000).toFixed(0)} m (illustrative)`;
  return `${km.toFixed(3)} km (illustrative)`;
}

async function findRoute() {
  if (isBusy || !campusGraph) return;
  const source = Number(sourceEl.value);
  const target = Number(targetEl.value);
  const algorithm = algorithmEl.value;

  if (source === target) {
    statusEl.textContent = "Choose two different locations.";
    return;
  }

  isBusy = true;
  findButton.disabled = true;
  statusEl.textContent = "Calculating shortest path…";

  try {
    const response = await fetch("/api/route", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source, target, algorithm })
    });

    const result = await response.json();
    if (!response.ok) throw new Error(result.detail || `Route API returned HTTP ${response.status}`);

    if (!result.found) {
      clearRoute();
      statusEl.textContent = "No route exists between these locations in the current graph.";
      resultEl.innerHTML = "<h2>Route details</h2><p>The selected locations are disconnected in graph.json.</p>";
      return;
    }

    drawRoute(result.nodes);
    const names = result.nodes.map(node => node.name);
    const distance = Number(result.distance_km);
    statusEl.textContent = `Route found · ${formatDistance(distance)} · ${result.explored_nodes} explored vertices`;

    resultEl.replaceChildren();
    const heading = document.createElement("h2");
    heading.textContent = "Route details";
    resultEl.appendChild(heading);

    const details = [
      ["Algorithm", algorithm === "dijkstra" ? "Dijkstra" : "Bidirectional Dijkstra"],
      ["Distance", formatDistance(distance)],
      ["Vertices explored", String(result.explored_nodes)],
      ["Execution time", `${Number(result.execution_ms).toFixed(4)} ms`],
      ["Path", names.join(" → ")]
    ];
    for (const [label, value] of details) {
      const p = document.createElement("p");
      const strong = document.createElement("strong");
      strong.textContent = `${label}: `;
      p.append(strong, document.createTextNode(value));
      resultEl.appendChild(p);
    }
  } catch (error) {
    clearRoute();
    statusEl.textContent = `Route calculation failed: ${error.message}`;
  } finally {
    isBusy = false;
    findButton.disabled = false;
  }
}

findButton.addEventListener("click", findRoute);
resetButton.addEventListener("click", () => {
  clearRoute();
  statusEl.textContent = campusGraph
    ? "Choose locations and calculate a route."
    : "Campus graph has not loaded.";
  resultEl.innerHTML = "<h2>Route details</h2><p>Select a start location and destination to calculate a route.</p>";
});

loadCampusGraph();
