def _priority_value(request_obj):
    raw_priority = request_obj.get("priority", 0)
    try:
        return int(raw_priority)
    except (TypeError, ValueError):
        return 0


def _estimated_time_value(request_obj):
    raw_time = request_obj.get("estimated_time")
    try:
        return float(raw_time)
    except (TypeError, ValueError):
        return float("inf")


def _normalize_text(value):
    return str(value or "").strip().lower()


def _resource_matches_complaint(complaint_type, resource_type):
    complaint = _normalize_text(complaint_type)
    resource = _normalize_text(resource_type)

    mapping = {
        "garbage": {"garbage", "truck"},
        "water": {"water", "tanker"},
        "medical": {"medical", "ambulance"},
    }

    for complaint_key, resource_tokens in mapping.items():
        if complaint_key in complaint:
            return any(token in resource for token in resource_tokens)

    return False


def priority_scheduler(requests, resources):
    """Assign free resources to highest numeric priority requests first."""
    if not requests or not resources:
        return []

    free_resources = [r for r in resources if _normalize_text(r.get("status")) == "free"]
    if not free_resources:
        return []

    sorted_requests = sorted(requests, key=_priority_value, reverse=True)

    assignments = []
    for req, res in zip(sorted_requests, free_resources):
        request_id = req.get("id")
        resource_id = res.get("id")
        if request_id is None or resource_id is None:
            continue
        assignments.append({"request_id": request_id, "resource_id": resource_id})

    return assignments


def sjf_scheduler(requests, resources):
    """Assign free resources to requests with shortest estimated_time first."""
    if not requests or not resources:
        return []

    free_resources = [r for r in resources if _normalize_text(r.get("status")) == "free"]
    if not free_resources:
        return []

    sorted_requests = sorted(requests, key=_estimated_time_value)

    assignments = []
    for req, res in zip(sorted_requests, free_resources):
        request_id = req.get("id")
        resource_id = res.get("id")
        if request_id is None or resource_id is None:
            continue
        assignments.append({"request_id": request_id, "resource_id": resource_id})

    return assignments


def greedy_scheduler(requests, resources):
    """Greedily assign first matching free resource based on complaint/resource type."""
    if not requests or not resources:
        return []

    available_resources = [r for r in resources if _normalize_text(r.get("status")) == "free"]
    if not available_resources:
        return []

    assignments = []
    for request_obj in requests:
        request_id = request_obj.get("id")
        if request_id is None:
            continue

        complaint_type = request_obj.get("complaint_type")
        match_index = None

        for idx, resource_obj in enumerate(available_resources):
            if _resource_matches_complaint(complaint_type, resource_obj.get("resource_type")):
                match_index = idx
                break

        if match_index is None:
            continue

        matched_resource = available_resources.pop(match_index)
        resource_id = matched_resource.get("id")
        if resource_id is None:
            continue

        assignments.append({"request_id": request_id, "resource_id": resource_id})

    return assignments
