import heapq

def dijkstra(graph, start, end):
    queue = [(0, start, [])]
    visited = set()

    while queue:
        (cost, node, path) = heapq.heappop(queue)
        if node in visited:
            continue

        path = path + [node]
        visited.add(node)

        if node == end:
            return (cost, path)

        for adj, weight in graph.get(node, {}).items():
            if adj not in visited:
                heapq.heappush(queue, (cost + weight, adj, path))

    return float("inf"), []


graph = {
    'A': {'B': 1, 'C': 4},
    'B': {'A': 1, 'C': 2, 'D': 5},
    'C': {'A': 4, 'B': 2, 'D': 1},
    'D': {'B': 5, 'C': 1}
}