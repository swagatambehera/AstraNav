#include <algorithm>
#include <chrono>
#include <cmath>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <queue>
#include <string>
#include <utility>
#include <vector>

using namespace std;

constexpr double INF = numeric_limits<double>::infinity();
constexpr double EARTH_RADIUS_KM = 6371.0;

// Graph structures
struct Node {
    int id;
    double lat, lon;
};

struct Edge {
    int to;
    double weight;
};

struct Graph {
    vector<Node> nodes;
    vector<vector<Edge>> adj;
};

struct Result {
    bool found = false;
    double distance = INF;
    vector<int> path;
    int explored = 0;
    double milliseconds = 0.0;
};

// Convert degrees to radians
static inline double toRadians(double degrees) {
    constexpr double PI = 3.14159265358979323846;
    return degrees * PI / 180.0;
}

// Haversine distance between two geographic coordinates
static double haversineKm(
    double lat1, double lon1,
    double lat2, double lon2
) {
    const double dLat = toRadians(lat2 - lat1);
    const double dLon = toRadians(lon2 - lon1);

    const double rLat1 = toRadians(lat1);
    const double rLat2 = toRadians(lat2);

    const double sinLat = sin(dLat / 2.0);
    const double sinLon = sin(dLon / 2.0);

    const double a =
        sinLat * sinLat +
        cos(rLat1) * cos(rLat2) *
        sinLon * sinLon;

    const double boundedA = max(0.0, min(1.0, a));

    return 2.0 * EARTH_RADIUS_KM *
           asin(sqrt(boundedA));
}

// Calculate a safe scale for the A* heuristic
static double calculateHeuristicScale(const Graph& g) {
    double scale = 1.0;

    for (int u = 0; u < (int)g.nodes.size(); ++u) {
        const Node& from = g.nodes[u];

        for (const Edge& edge : g.adj[u]) {
            const Node& to = g.nodes[edge.to];

            const double geoDistance = haversineKm(
                from.lat, from.lon,
                to.lat, to.lon
            );

            if (geoDistance > 0.0) {
                scale = min(
                    scale,
                    edge.weight / geoDistance
                );
            }
        }
    }

    return max(0.0, scale);
}

// Dijkstra and A* shortest-path engine
using QueueItem = pair<double, int>;

static Result shortestPath(
    const Graph& g,
    int source,
    int target,
    const string& algorithm
) {
    Result result;

    const int n = (int)g.nodes.size();

    // Validate source and destination
    if (source < 0 || target < 0 ||
        source >= n || target >= n) {
        return result;
    }

    // Precompute heuristic values
    vector<double> h(n, 0.0);

    if (algorithm == "astar") {
        const double scale = calculateHeuristicScale(g);
        const Node& destination = g.nodes[target];

        for (int i = 0; i < n; ++i) {
            h[i] = scale * haversineKm(
                g.nodes[i].lat,
                g.nodes[i].lon,
                destination.lat,
                destination.lon
            );
        }
    }

    // Initialize shortest-path data
    vector<double> dist(n, INF);
    vector<int> parent(n, -1);
    vector<bool> closed(n, false);

    // Min-priority queue
    priority_queue<
        QueueItem,
        vector<QueueItem>,
        greater<QueueItem>
    > pq;

    dist[source] = 0.0;

    // Start measuring search execution time
    const auto start = chrono::steady_clock::now();

    pq.push({h[source], source});

    while (!pq.empty()) {
        const QueueItem current = pq.top();
        pq.pop();

        const double priority = current.first;
        const int u = current.second;

        // Skip outdated queue entries
        if (priority > dist[u] + h[u]) {
            continue;
        }

        // Skip already processed vertices
        if (closed[u]) {
            continue;
        }

        closed[u] = true;
        result.explored++;

        // Destination reached
        if (u == target) {
            break;
        }

        // Explore adjacent vertices
        for (const Edge& edge : g.adj[u]) {
            const int v = edge.to;

            if (closed[v]) {
                continue;
            }

            // Edge relaxation
            const double candidate = dist[u] + edge.weight;

            if (candidate < dist[v]) {
                dist[v] = candidate;
                parent[v] = u;

                // Push updated priority
                pq.push({
                    candidate + h[v],
                    v
                });
            }
        }
    }

    // End search timer
    const auto end = chrono::steady_clock::now();

    result.milliseconds =
        chrono::duration<double, milli>(end - start).count();

    // Check whether destination is reachable
    if (!isfinite(dist[target])) {
        return result;
    }

    result.found = true;
    result.distance = dist[target];

    // Reconstruct shortest path
    for (int v = target; v != -1; v = parent[v]) {
        result.path.push_back(v);
    }

    reverse(result.path.begin(), result.path.end());

    return result;
}

// Main function
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m, source, target;
    string algorithm;

    // Read request header
    if (!(cin >> n >> m >> source >> target >> algorithm)) {
        cerr << "Invalid request header\n";
        return 2;
    }

    // Validate graph dimensions
    if (n <= 0 || m < 0 ||
        n > 1000000 || m > 5000000) {
        cerr << "Invalid graph dimensions\n";
        return 2;
    }

    // Validate source and destination
    if (source < 0 || source >= n ||
        target < 0 || target >= n) {
        cerr << "Invalid source or target\n";
        return 2;
    }

    // Validate algorithm
    if (algorithm != "dijkstra" && algorithm != "astar") {
        cerr << "Unknown algorithm\n";
        return 2;
    }

    Graph g;
    g.nodes.resize(n);
    g.adj.resize(n);

    vector<bool> nodeSeen(n, false);

    // Read vertices
    for (int i = 0; i < n; ++i) {
        int id;
        double lat, lon;

        if (!(cin >> id >> lat >> lon) ||
            id < 0 || id >= n ||
            !isfinite(lat) || !isfinite(lon) ||
            lat < -90.0 || lat > 90.0 ||
            lon < -180.0 || lon > 180.0 ||
            nodeSeen[id]) {

            cerr << "Invalid node record\n";
            return 2;
        }

        nodeSeen[id] = true;
        g.nodes[id] = {id, lat, lon};
    }

    // Read directed edges
    for (int i = 0; i < m; ++i) {
        int from, to;
        double weight;

        if (!(cin >> from >> to >> weight) ||
            from < 0 || from >= n ||
            to < 0 || to >= n ||
            !isfinite(weight) || weight < 0.0) {

            cerr << "Invalid edge record\n";
            return 2;
        }

        g.adj[from].push_back({to, weight});
    }

    // Execute selected algorithm
    const Result r = shortestPath(
        g, source, target, algorithm
    );

    // Generate JSON response
    cout << fixed << setprecision(8);

    cout << "{\"found\":"
         << (r.found ? "true" : "false")

         << ",\"distance_km\":"
         << (r.found ? r.distance : 0.0)

         << ",\"explored_nodes\":"
         << r.explored

         << ",\"execution_ms\":"
         << r.milliseconds

         << ",\"path\":[";

    for (size_t i = 0; i < r.path.size(); ++i) {
        if (i > 0) {
            cout << ",";
        }

        cout << r.path[i];
    }

    cout << "]}\n";

    return 0;
}
