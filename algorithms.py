import heapq
from typing import Dict, List, Tuple, Set
import math

class Graph:
    def __init__(self):
        self.graph: Dict[str, Dict[str, float]] = {}
        self.coordinates: Dict[str, Tuple[float, float]] = {}  # For A* algorithm

    def add_edge(self, from_node: str, to_node: str, weight: float):
        if from_node not in self.graph:
            self.graph[from_node] = {}
        if to_node not in self.graph:
            self.graph[to_node] = {}
        self.graph[from_node][to_node] = weight
        self.graph[to_node][from_node] = weight  # Assuming undirected graph

    def add_coordinate(self, node: str, x: float, y: float):
        self.coordinates[node] = (x, y)

    def dijkstra(self, start: str, end: str) -> Tuple[float, List[str]]:
        """
        Dijkstra's algorithm implementation for finding shortest path.
        Returns tuple of (total_cost, path).
        """
        distances = {node: float('infinity') for node in self.graph}
        distances[start] = 0
        previous = {node: None for node in self.graph}
        queue = [(0, start)]

        while queue:
            current_distance, current_node = heapq.heappop(queue)

            if current_node == end:
                path = []
                while current_node is not None:
                    path.append(current_node)
                    current_node = previous[current_node]
                return current_distance, path[::-1]

            if current_distance > distances[current_node]:
                continue

            for neighbor, weight in self.graph[current_node].items():
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_node
                    heapq.heappush(queue, (distance, neighbor))

        return float('infinity'), []

    def bellman_ford(self, start: str, end: str) -> Tuple[float, List[str]]:
        """
        Bellman-Ford algorithm implementation for finding shortest path.
        Can handle negative weights but not negative cycles.
        Returns tuple of (total_cost, path).
        """
        distances = {node: float('infinity') for node in self.graph}
        distances[start] = 0
        previous = {node: None for node in self.graph}

        # Relax edges repeatedly
        for _ in range(len(self.graph) - 1):
            for node in self.graph:
                for neighbor, weight in self.graph[node].items():
                    if distances[node] + weight < distances[neighbor]:
                        distances[neighbor] = distances[node] + weight
                        previous[neighbor] = node

        # Check for negative cycles
        for node in self.graph:
            for neighbor, weight in self.graph[node].items():
                if distances[node] + weight < distances[neighbor]:
                    raise ValueError("Graph contains negative cycle")

        # Reconstruct path
        if distances[end] == float('infinity'):
            return float('infinity'), []

        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        return distances[end], path[::-1]

    def heuristic(self, node: str, end: str) -> float:
        """
        Calculate heuristic (Euclidean distance) for A* algorithm.
        """
        if node not in self.coordinates or end not in self.coordinates:
            return 0
        x1, y1 = self.coordinates[node]
        x2, y2 = self.coordinates[end]
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def a_star(self, start: str, end: str) -> Tuple[float, List[str]]:
        """
        A* algorithm implementation for finding shortest path.
        Uses Euclidean distance as heuristic.
        Returns tuple of (total_cost, path).
        """
        if start not in self.coordinates or end not in self.coordinates:
            raise ValueError("Start and end nodes must have coordinates for A*")

        g_score = {node: float('infinity') for node in self.graph}
        g_score[start] = 0
        f_score = {node: float('infinity') for node in self.graph}
        f_score[start] = self.heuristic(start, end)
        previous = {node: None for node in self.graph}

        open_set = [(f_score[start], start)]
        closed_set = set()

        while open_set:
            current_f, current = heapq.heappop(open_set)

            if current == end:
                path = []
                while current is not None:
                    path.append(current)
                    current = previous[current]
                return g_score[end], path[::-1]

            closed_set.add(current)

            for neighbor, weight in self.graph[current].items():
                if neighbor in closed_set:
                    continue

                tentative_g_score = g_score[current] + weight

                if tentative_g_score < g_score[neighbor]:
                    previous[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return float('infinity'), []

# Example usage
if __name__ == "__main__":
    # Create a sample graph
    g = Graph()
    
    # Add edges (representing roads/connections)
    g.add_edge('A', 'B', 4)
    g.add_edge('A', 'C', 2)
    g.add_edge('B', 'D', 3)
    g.add_edge('C', 'D', 1)
    g.add_edge('C', 'E', 5)
    g.add_edge('D', 'E', 2)
    
    # Add coordinates for A* algorithm
    g.add_coordinate('A', 0, 0)
    g.add_coordinate('B', 4, 0)
    g.add_coordinate('C', 2, 2)
    g.add_coordinate('D', 4, 4)
    g.add_coordinate('E', 6, 2)
    
    # Test all algorithms
    start_node = 'A'
    end_node = 'E'
    
    print("Dijkstra's Algorithm:")
    cost, path = g.dijkstra(start_node, end_node)
    print(f"Cost: {cost}, Path: {' -> '.join(path)}")
    
    print("\nBellman-Ford Algorithm:")
    cost, path = g.bellman_ford(start_node, end_node)
    print(f"Cost: {cost}, Path: {' -> '.join(path)}")
    
    print("\nA* Algorithm:")
    cost, path = g.a_star(start_node, end_node)
    print(f"Cost: {cost}, Path: {' -> '.join(path)}") 