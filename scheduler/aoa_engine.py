def build_aoa_graph(requests, resources=None):
    """Build a directed request-order graph from in-memory request inputs only."""
    if not requests:
        return {"nodes": [], "edges": []}

    nodes = []
    edges = []

    for index, request_obj in enumerate(requests):
        request_id = request_obj.get("id")
        node_id = request_id if request_id is not None else index
        nodes.append(
            {
                "id": node_id,
                "request_id": request_id,
                "complaint_type": request_obj.get("complaint_type") or request_obj.get("type"),
                "priority": request_obj.get("priority"),
                "estimated_time": request_obj.get("estimated_time"),
                "order": index,
            }
        )

    for index in range(len(nodes) - 1):
        edges.append(
            {
                "from": nodes[index]["id"],
                "to": nodes[index + 1]["id"],
                "relation": "next",
            }
        )

    return {"nodes": nodes, "edges": edges}

