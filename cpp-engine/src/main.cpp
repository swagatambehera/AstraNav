#include <cctype>
#include <algorithm>
#include <chrono>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <queue>
#include <string>
#include <utility>
#include <vector>

using namespace std;

constexpr double INF = numeric_limits<double>::infinity();
using QueueItem = pair<double, int>;
using MinPriorityQueue =
    priority_queue<QueueItem, vector<QueueItem>, greater<QueueItem>>;

struct Node {
    int id = -1;
    double lat = 0.0;
    double lon = 0.0;
};

struct Edge {
    int to;
    double weight;
};

struct Graph {
    vector<Node> nodes;
    vector<vector<Edge>> adj;
    vector<vector<Edge>> reverseAdj;
};

struct Result {
    bool found = false;
    double distance = INF;
    vector<int> path;
    int explored = 0;
    double milliseconds = 0.0;
};

static void cleanQueue(
    MinPriorityQueue& pq,
    const vector<double>& dist,
    const vector<bool>& settled
) {
    while (!pq.empty()) {
        const QueueItem item = pq.top();
        const double key = item.first;
        const int vertex = item.second;

        if (settled[vertex] || key > dist[vertex]) {
            pq.pop();
        } else {
            break;
        }
    }
}

static Result runDijkstra(const Graph& graph, int source, int target) {
    Result result;
    const int n = static_cast<int>(graph.nodes.size());

    vector<double> dist(n, INF);
    vector<int> parent(n, -1);
    vector<bool> settled(n, false);
    MinPriorityQueue pq;

    const auto start = chrono::steady_clock::now();

    dist[source] = 0.0;
    pq.push({0.0, source});

    while (!pq.empty()) {
        const QueueItem item = pq.top();
        const double distance = item.first;
        const int u = item.second;
        pq.pop();

        if (settled[u] || distance > dist[u]) {
            continue;
        }

        settled[u] = true;
        ++result.explored;

        if (u == target) {
            break;
        }

        for (const Edge& edge : graph.adj[u]) {
            const int v = edge.to;
            const double candidate = dist[u] + edge.weight;

            if (!settled[v] && candidate < dist[v]) {
                dist[v] = candidate;
                parent[v] = u;
                pq.push({candidate, v});
            }
        }
    }

    const auto end = chrono::steady_clock::now();
    result.milliseconds =
        chrono::duration<double, milli>(end - start).count();

    if (!isfinite(dist[target])) {
        return result;
    }

    result.found = true;
    result.distance = dist[target];

    for (int v = target; v != -1; v = parent[v]) {
        result.path.push_back(v);
    }
    reverse(result.path.begin(), result.path.end());

    return result;
}

// Bidirectional Dijkstra uses the original graph in the forward direction
// and reverseAdj in the backward direction.
static Result runBidirectionalDijkstra(
    const Graph& graph,
    int source,
    int target
) {
    Result result;
    const int n = static_cast<int>(graph.nodes.size());

    if (source == target) {
        result.found = true;
        result.distance = 0.0;
        result.path.push_back(source);
        result.explored = 1;
        return result;
    }

    vector<double> distForward(n, INF);
    vector<double> distBackward(n, INF);
    vector<int> parentForward(n, -1);
    vector<int> nextBackward(n, -1);
    vector<bool> settledForward(n, false);
    vector<bool> settledBackward(n, false);

    MinPriorityQueue pqForward;
    MinPriorityQueue pqBackward;

    double bestDistance = INF;
    int meetingVertex = -1;

    const auto updateBest = [&](int vertex) {
        if (isfinite(distForward[vertex]) &&
            isfinite(distBackward[vertex])) {
            const double candidate =
                distForward[vertex] + distBackward[vertex];

            if (candidate < bestDistance) {
                bestDistance = candidate;
                meetingVertex = vertex;
            }
        }
    };

    const auto start = chrono::steady_clock::now();

    distForward[source] = 0.0;
    distBackward[target] = 0.0;
    pqForward.push({0.0, source});
    pqBackward.push({0.0, target});

    while (true) {
        cleanQueue(pqForward, distForward, settledForward);
        cleanQueue(pqBackward, distBackward, settledBackward);

        const double minForward =
            pqForward.empty() ? INF : pqForward.top().first;
        const double minBackward =
            pqBackward.empty() ? INF : pqBackward.top().first;

        // No remaining pair of frontier distances can improve bestDistance.
        if (minForward + minBackward >= bestDistance) {
            break;
        }

        if (pqForward.empty() || pqBackward.empty()) {
            break;
        }

        // Expand the frontier with the smaller minimum tentative distance.
        if (minForward <= minBackward) {
            const QueueItem item = pqForward.top();
            const double distance = item.first;
            const int u = item.second;
            pqForward.pop();

            if (settledForward[u] || distance > distForward[u]) {
                continue;
            }

            settledForward[u] = true;
            ++result.explored;
            updateBest(u);

            for (const Edge& edge : graph.adj[u]) {
                const int v = edge.to;
                const double candidate = distForward[u] + edge.weight;

                if (!settledForward[v] && candidate < distForward[v]) {
                    distForward[v] = candidate;
                    parentForward[v] = u;
                    pqForward.push({candidate, v});
                }

                updateBest(v);
            }
        } else {
            const QueueItem item = pqBackward.top();
            const double distance = item.first;
            const int v = item.second;
            pqBackward.pop();

            if (settledBackward[v] || distance > distBackward[v]) {
                continue;
            }

            settledBackward[v] = true;
            ++result.explored;
            updateBest(v);

            // reverseAdj[v] contains original incoming edges u -> v.
            for (const Edge& reverseEdge : graph.reverseAdj[v]) {
                const int u = reverseEdge.to;
                const double candidate =
                    distBackward[v] + reverseEdge.weight;

                if (!settledBackward[u] && candidate < distBackward[u]) {
                    distBackward[u] = candidate;
                    nextBackward[u] = v;
                    pqBackward.push({candidate, u});
                }

                updateBest(u);
            }
        }
    }

    const auto end = chrono::steady_clock::now();
    result.milliseconds =
        chrono::duration<double, milli>(end - start).count();

    if (meetingVertex == -1 || !isfinite(bestDistance)) {
        return result;
    }

    // Reconstruct source -> meeting vertex.
    vector<int> left;
    for (int v = meetingVertex; v != -1; v = parentForward[v]) {
        left.push_back(v);
    }
    reverse(left.begin(), left.end());

    // Reconstruct meeting vertex -> target.
    result.path = left;
    int current = meetingVertex;

    while (current != target) {
        current = nextBackward[current];

        if (current == -1) {
            result.path.clear();
            return result;
        }

        result.path.push_back(current);
    }

    result.found = true;
    result.distance = bestDistance;
    return result;
}

static string normalizeAlgorithm(string algorithm) {
    transform(
        algorithm.begin(),
        algorithm.end(),
        algorithm.begin(),
        [](unsigned char c) {
            if (c == '-') return '_';
            if (c == ' ') return '_';
            return static_cast<char>(tolower(c));
        }
    );

    return algorithm;
}

static Result shortestPath(
    const Graph& graph,
    int source,
    int target,
    const string& algorithm
) {
    if (algorithm == "dijkstra") {
        return runDijkstra(graph, source, target);
    }

    if (algorithm == "bidirectional_dijkstra") {
        return runBidirectionalDijkstra(graph, source, target);
    }

    return Result{};
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m, source, target;
    string algorithm;

    if (!(cin >> n >> m >> source >> target >> algorithm)) {
        cerr << "Invalid request header\n";
        return 2;
    }

    algorithm = normalizeAlgorithm(algorithm);

    if (n <= 0 || m < 0 || n > 1000000 || m > 5000000) {
        cerr << "Invalid graph dimensions\n";
        return 2;
    }

    if (source < 0 || source >= n || target < 0 || target >= n) {
        cerr << "Invalid source or target\n";
        return 2;
    }

    if (algorithm != "dijkstra" &&
        algorithm != "bidirectional_dijkstra") {
        cerr << "Unknown algorithm: " << algorithm << '\n';
        return 2;
    }

    Graph graph;
    graph.nodes.resize(n);
    graph.adj.resize(n);
    graph.reverseAdj.resize(n);

    vector<bool> nodeSeen(n, false);

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
        graph.nodes[id] = {id, lat, lon};
    }

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

        graph.adj[from].push_back({to, weight});
        graph.reverseAdj[to].push_back({from, weight});
    }

    const Result result =
        shortestPath(graph, source, target, algorithm);

    cout << fixed << setprecision(8);

    cout << "{\"found\":" << (result.found ? "true" : "false")
         << ",\"distance_km\":" << (result.found ? result.distance : 0.0)
         << ",\"explored_nodes\":" << result.explored
         << ",\"execution_ms\":" << result.milliseconds
         << ",\"path\":[";

    for (size_t i = 0; i < result.path.size(); ++i) {
        if (i > 0) {
            cout << ',';
        }
        cout << result.path[i];
    }

    cout << "]}\n";
    return 0;
}
