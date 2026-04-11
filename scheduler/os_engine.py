CLASS_CRITICAL = "CRITICAL"
CLASS_HIGH = "HIGH"
CLASS_NORMAL = "NORMAL"
CLASS_LOW = "LOW"

CLASS_ORDER = [CLASS_CRITICAL, CLASS_HIGH, CLASS_NORMAL, CLASS_LOW]

CLASS_OF_SERVICE_MAP = {
    CLASS_CRITICAL: {"ambulance", "fire_service"},
    CLASS_HIGH: {"police"},
    CLASS_NORMAL: {"agriculture_officer"},
    CLASS_LOW: {"garbage_truck"},
}

DEFAULT_STARVATION_THRESHOLD_MINUTES = 30
DEFAULT_AGING_STEP_MINUTES = 15


def _priority_value(request_obj):
    raw_priority = request_obj.get("priority", 0)
    try:
        return int(raw_priority)
    except (TypeError, ValueError):
        return 0


def _estimated_time_value(request_obj):
    raw_time = request_obj.get("execution_time", request_obj.get("estimated_time"))
    try:
        return float(raw_time)
    except (TypeError, ValueError):
        return float("inf")


def _waiting_time_value(request_obj):
    raw_waiting = request_obj.get("waiting_time", 0)
    try:
        return max(0, int(raw_waiting))
    except (TypeError, ValueError):
        return 0


def _normalize_text(value):
    return str(value or "").strip().lower()


def normalize_resource_type(resource_type):
    """Convert legacy resource labels into canonical scheduler resource types."""
    resource = _normalize_text(resource_type).replace("-", "_").replace(" ", "_")

    if "ambulance" in resource or "medical" in resource:
        return "ambulance"
    if "fire" in resource:
        return "fire_service"
    if "police" in resource:
        return "police"
    if "agriculture" in resource:
        return "agriculture_officer"
    if "garbage" in resource:
        return "garbage_truck"

    return resource or "agriculture_officer"


def get_class_of_service(resource_type):
    """Map resource_type to service class: CRITICAL/HIGH/NORMAL/LOW."""
    normalized = normalize_resource_type(resource_type)

    for class_name, resource_types in CLASS_OF_SERVICE_MAP.items():
        if normalized in resource_types:
            return class_name

    return CLASS_NORMAL


def _class_from_resource_type(resource_type):
    resource = normalize_resource_type(resource_type)

    return get_class_of_service(resource)


def _class_of_service(request_obj):
    provided = _normalize_text(request_obj.get("class_of_service"))
    if provided:
        normalized = provided.upper()
        if normalized in CLASS_ORDER:
            return normalized

    resource_type = request_obj.get("resource_type") or request_obj.get("complaint_type") or request_obj.get("type")
    return get_class_of_service(resource_type)


def _effective_priority(
    request_obj,
    starvation_threshold_minutes=DEFAULT_STARVATION_THRESHOLD_MINUTES,
    aging_step_minutes=DEFAULT_AGING_STEP_MINUTES,
):
    """Increase priority for long-waiting requests to reduce starvation."""
    base_priority = _priority_value(request_obj)
    waiting_minutes = _waiting_time_value(request_obj)

    if waiting_minutes <= starvation_threshold_minutes:
        return base_priority

    effective_step = max(1, int(aging_step_minutes))
    bonus = 1 + ((waiting_minutes - starvation_threshold_minutes) // effective_step)
    return base_priority + bonus


def _resource_matches_complaint(complaint_type, resource_type):
    complaint = normalize_resource_type(complaint_type)
    resource = normalize_resource_type(resource_type)

    mapping = {
        "garbage_truck": {"garbage_truck"},
        "water_tanker": {"water_tanker"},
        "ambulance": {"ambulance"},
        "fire_service": {"fire_service"},
        "police": {"police"},
        "agriculture_officer": {"agriculture_officer"},
    }

    for complaint_key, allowed_resources in mapping.items():
        if complaint == complaint_key:
            return resource in allowed_resources

    return False


def determine_highest_class(requests):
    """Return the highest available class from pending requests."""
    if not requests:
        return None

    classes_present = {_class_of_service(req) for req in requests}
    for class_name in CLASS_ORDER:
        if class_name in classes_present:
            return class_name

    return None


def filter_requests_by_class(requests, class_name):
    """Keep only requests that belong to the selected class of service."""
    if not requests or not class_name:
        return []
    return [req for req in requests if _class_of_service(req) == class_name]


def _assign_by_sorted_order(sorted_requests, free_resources):
    assignments = []
    for req, res in zip(sorted_requests, free_resources):
        request_id = req.get("id")
        resource_id = res.get("id")
        if request_id is None or resource_id is None:
            continue
        assignments.append({"request_id": request_id, "resource_id": resource_id})
    return assignments


def _greedy_assign(requests, free_resources):
    available_resources = list(free_resources)
    assignments = []

    for request_obj in requests:
        request_id = request_obj.get("id")
        if request_id is None:
            continue

        complaint_type = request_obj.get("complaint_type") or request_obj.get("type")
        match_index = None

        for idx, resource_obj in enumerate(available_resources):
            if _resource_matches_complaint(complaint_type, resource_obj.get("resource_type") or resource_obj.get("type")):
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


def apply_selected_algorithm_within_class(
    requests,
    resources,
    algorithm,
    starvation_threshold_minutes=DEFAULT_STARVATION_THRESHOLD_MINUTES,
    aging_step_minutes=DEFAULT_AGING_STEP_MINUTES,
):
    """Apply the selected algorithm only within the already-selected class."""
    if not requests or not resources:
        return []

    free_resources = [r for r in resources if _normalize_text(r.get("status")) == "free"]
    if not free_resources:
        return []

    selected_algorithm = _normalize_text(algorithm) or "priority"

    if selected_algorithm == "priority":
        sorted_requests = sorted(
            requests,
            key=lambda req: (
                _effective_priority(req, starvation_threshold_minutes, aging_step_minutes),
                _waiting_time_value(req),
                -_estimated_time_value(req),
            ),
            reverse=True,
        )
        return _assign_by_sorted_order(sorted_requests, free_resources)

    if selected_algorithm == "sjf":
        sorted_requests = sorted(
            requests,
            key=lambda req: (
                _estimated_time_value(req),
                -_effective_priority(req, starvation_threshold_minutes, aging_step_minutes),
                -_waiting_time_value(req),
            ),
        )
        return _assign_by_sorted_order(sorted_requests, free_resources)

    if selected_algorithm == "greedy":
        return _greedy_assign(requests, free_resources)

    return []


def multi_level_scheduler(
    requests,
    resources,
    algorithm="priority",
    starvation_threshold_minutes=DEFAULT_STARVATION_THRESHOLD_MINUTES,
    aging_step_minutes=DEFAULT_AGING_STEP_MINUTES,
):
    """
    Multi-level scheduling:
    1) Select highest class (CRITICAL > HIGH > NORMAL > LOW)
    2) Schedule only requests in that class using the chosen algorithm
    """
    if not requests or not resources:
        return []

    highest_class = determine_highest_class(requests)
    if highest_class is None:
        return []

    class_requests = filter_requests_by_class(requests, highest_class)
    if not class_requests:
        return []

    return apply_selected_algorithm_within_class(
        class_requests,
        resources,
        algorithm,
        starvation_threshold_minutes=starvation_threshold_minutes,
        aging_step_minutes=aging_step_minutes,
    )


def priority_scheduler(requests, resources):
    """Backward-compatible priority scheduler constrained to highest class."""
    return multi_level_scheduler(requests, resources, algorithm="priority")


def sjf_scheduler(requests, resources):
    """Backward-compatible SJF scheduler constrained to highest class."""
    return multi_level_scheduler(requests, resources, algorithm="sjf")


def greedy_scheduler(requests, resources):
    """Backward-compatible greedy scheduler constrained to highest class."""
    return multi_level_scheduler(requests, resources, algorithm="greedy")

