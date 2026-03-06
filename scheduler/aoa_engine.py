def build_aoa_graph(requests, resources):
    """
    Build an Activity-On-Arrow (AOA) graph representation of scheduling requests.
    
    In AOA:
    - Nodes represent events (start/end points)
    - Edges represent activities (the requests)
    - Graph is sequential: Node0 → Node1 → Node2 → ...
    
    Args:
        requests: List of dictionaries, each containing:
            - id: request identifier
            - type: request type (e.g., "Garbage", "Water", "Medical")
            - priority: priority level (optional)
            - estimated_time: estimated duration
        resources: List of dictionaries (available resources)
            - Note: Resources are not used in AOA graph construction,
              they are only needed for actual scheduling
    
    Returns:
        Dictionary with adjacency structure:
        {
            "nodes": [0, 1, 2, ...],
            "edges": [
                {"from": 0, "to": 1, "request_id": x, "type": "...", "time": y},
                ...
            ]
        }
    
    Edge Cases:
        - Empty requests list: returns {"nodes": [], "edges": []}
        - Empty resources: still builds graph from requests
        - More requests than resources: includes all requests in graph
    """
    # Handle edge case: empty requests list
    if not requests:
        return {"nodes": [], "edges": []}
    
    # Build nodes list - sequential from 0 to len(requests)
    # Number of nodes = number of requests + 1 (start node + one per request)
    num_nodes = len(requests) + 1
    nodes = list(range(num_nodes))
    
    # Build edges list - each request becomes an edge
    # Edge goes from node i to node i+1 for request at index i
    edges = []
    for index, request in enumerate(requests):
        edge = {
            "from": index,           # Start at current node
            "to": index + 1,        # End at next node
            "request_id": request.get("id"),
            "type": request.get("type", ""),
            "time": request.get("estimated_time", 0)
        }
        edges.append(edge)
    
    # Return the AOA graph structure
    return {
        "nodes": nodes,
        "edges": edges
    }


def priority_scheduler(requests, resources):
    """
    requests: list of dicts
    resources: list of dicts
    Returns:
        list of {"request_id": x, "resource_id": y}
    """
    return []


def sjf_scheduler(requests, resources):
    return []


def greedy_scheduler(requests, resources):
    return []

