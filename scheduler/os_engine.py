def priority_scheduler(requests, resources):
    """
    requests: list of dicts
    resources: list of dicts
    Returns:
        list of {"request_id": x, "resource_id": y}
    """
    if not requests or not resources:
        return []

    # Priority ranking
    priority_rank = {
        "High": 3,
        "Medium": 2,
        "Low": 1
    }

    # Get only free resources
    free_resources = [
        r for r in resources if r.get("status") == "free"
    ]

    if not free_resources:
        return []

    # Sort requests by priority (highest first)
    sorted_requests = sorted(
        requests,
        key=lambda r: priority_rank.get(r.get("priority"), 0),
        reverse=True
    )

    assignments = []

    # Assign resources sequentially
    for req, res in zip(sorted_requests, free_resources):
        assignments.append({
            "request_id": req.get("id"),
            "resource_id": res.get("id")
        })

    return assignments



def sjf_scheduler(requests, resources):
    
    if not requests or not resources:
        return []

    # Get free resources
    free_resources = [
        r for r in resources if r.get("status") == "free"
    ]

    if not free_resources:
        return []

    # Sort by estimated execution time
    sorted_requests = sorted(
        requests,
        key=lambda r: r.get("estimated_time", float("inf"))
    )

    assignments = []

    for req, res in zip(sorted_requests, free_resources):
        assignments.append({
            "request_id": req.get("id"),
            "resource_id": res.get("id")
        })

    return assignments
    


def greedy_scheduler(requests, resources):
    return []
