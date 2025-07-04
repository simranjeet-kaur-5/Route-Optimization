import heapq
from typing import Dict, List, Tuple, Optional
import osmnx as ox
import networkx as nx

def get_shortest_path(source_lat, source_lon, dest_lat, dest_lon):
    # Get the driving graph around the source point
    G = ox.graph_from_point((source_lat, source_lon), dist=10000, network_type='drive')

    # Get nearest nodes in the graph to source and destination
    source_node = ox.distance.nearest_nodes(G, source_lon, source_lat)
    dest_node = ox.distance.nearest_nodes(G, dest_lon, dest_lat)

    # Compute shortest path using Dijkstra's algorithm
    route = nx.shortest_path(G, source=source_node, target=dest_node, weight='length')

    # Get total distance in meters
    distance = nx.shortest_path_length(G, source=source_node, target=dest_node, weight='length')

    return route, distance / 1000  # return distance in kilometers

def find_shortest_path(graph: Dict[str, Dict[str, float]], start: str, end: str) -> Tuple[float, List[str]]:
    """
    Find the shortest path between two nodes in a graph using Dijkstra's algorithm.
    
    Args:
        graph: Dictionary representing the graph where keys are nodes and values are dictionaries
              of neighboring nodes and their distances
        start: Starting node
        end: Destination node
    
    Returns:
        Tuple containing (total_distance, path)
    """
    if start not in graph or end not in graph:
        return float('inf'), []

    # Initialize distances and previous nodes
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    previous = {node: None for node in graph}
    
    # Priority queue for Dijkstra's algorithm
    queue = [(0, start)]
    
    while queue:
        current_distance, current_node = heapq.heappop(queue)
        
        # If we've reached the end node, we can stop
        if current_node == end:
            break
            
        # If we've already found a shorter path to this node, skip it
        if current_distance > distances[current_node]:
            continue
            
        # Check all neighbors of the current node
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            
            # If we found a shorter path to the neighbor, update it
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))
    
    # If we couldn't reach the end node
    if distances[end] == float('inf'):
        return float('inf'), []
    
    # Reconstruct the path
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = previous[current]
    
    return distances[end], path[::-1]  # Return distance and reversed path
