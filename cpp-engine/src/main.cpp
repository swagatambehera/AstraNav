#include <algorithm>
#include <chrono>
#include <cmath>
#include <iostream>
#include <limits>
#include <queue>
#include <string>
#include <vector>
#include <iomanip>
using namespace std;

struct Node { int id; double lat, lon; };
struct Edge { int to; double weight; };
struct Graph { vector<Node> nodes; vector<vector<Edge>> adj; };

static double haversineKm(double lat1, double lon1, double lat2, double lon2) {
    constexpr double R = 6371.0;
    constexpr double PI = 3.14159265358979323846;
    auto rad = [PI](double d) { return d * PI / 180.0; };
    double dLat = rad(lat2-lat1), dLon = rad(lon2-lon1);
    double a = sin(dLat/2)*sin(dLat/2) +
        cos(rad(lat1))*cos(rad(lat2))*sin(dLon/2)*sin(dLon/2);
    return 2.0 * R * asin(min(1.0, sqrt(a)));
}
struct Result {
    bool found = false;
    double distance = numeric_limits<double>::infinity();
    vector<int> path;
    int explored = 0;
    double milliseconds = 0.0;
};

static Result shortestPath(const Graph& g, int source, int target, const string& algorithm) {
    Result result;
    if (source < 0 || target < 0 || source >= (int)g.nodes.size() || target >= (int)g.nodes.size()) return result;
    const int n = (int)g.nodes.size();
    const double INF = numeric_limits<double>::infinity();
    vector<double> dist(n, INF);
    vector<int> parent(n, -1);
    vector<bool> closed(n, false);
    using Item = pair<double,int>;
    priority_queue<Item, vector<Item>, greater<Item>> pq;
    dist[source] = 0.0;
    auto heuristic = [&](int v) {
        if (algorithm != "astar") return 0.0;
        const auto& a = g.nodes[v]; const auto& b = g.nodes[target];
        return haversineKm(a.lat,a.lon,b.lat,b.lon);
    };
    auto start = chrono::steady_clock::now();
    pq.push(Item(heuristic(source), source));
    while (!pq.empty()) {
        const Item current = pq.top();
        pq.pop();
        const double priority = current.first;
        const int u = current.second;
        (void)priority;
        if (closed[u]) continue;
        closed[u] = true;
        result.explored++;
        if (u == target) break;
        for (const auto& e : g.adj[u]) {
            if (closed[e.to]) continue;
            double candidate = dist[u] + e.weight;
            if (candidate < dist[e.to]) {
                dist[e.to] = candidate;
                parent[e.to] = u;
                pq.push(Item(candidate + heuristic(e.to), e.to));
            }
        }
    }
    auto end = chrono::steady_clock::now();
    result.milliseconds = chrono::duration<double,milli>(end-start).count();
    if (!isfinite(dist[target])) return result;
    result.found = true; result.distance = dist[target];
    for (int v=target; v!=-1; v=parent[v]) result.path.push_back(v);
    reverse(result.path.begin(), result.path.end());
    return result;
}
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n,m,source,target; string algorithm;
    if (!(cin>>n>>m>>source>>target>>algorithm)) { cerr<<"Invalid request header\n"; return 2; }
    Graph g; g.nodes.resize(n); g.adj.resize(n);
    for (int i=0;i<n;i++) {
        int id; double lat,lon;
        if (!(cin>>id>>lat>>lon) || id<0 || id>=n) { cerr<<"Invalid node record\n"; return 2; }
        g.nodes[id]={id,lat,lon};
    }
    for (int i=0;i<m;i++) {
        int from,to; double w;
        if (!(cin>>from>>to>>w) || from<0 || to<0 || from>=n || to>=n || w<0) {
            cerr<<"Invalid edge record\n"; return 2;
        }
        g.adj[from].push_back({to,w});
    }
    if (algorithm!="dijkstra" && algorithm!="astar") { cerr<<"Unknown algorithm\n"; return 2; }
    Result r=shortestPath(g,source,target,algorithm);
    cout<<fixed<<setprecision(8);
    cout<<"{\"found\":"<<(r.found?"true":"false")
        <<",\"distance_km\":"<<(r.found?r.distance:0.0)
        <<",\"explored_nodes\":"<<r.explored
        <<",\"execution_ms\":"<<r.milliseconds<<",\"path\":[";
    for(size_t i=0;i<r.path.size();i++){if(i)cout<<",";cout<<r.path[i];}
    cout<<"]}\n";
    return 0;
}
