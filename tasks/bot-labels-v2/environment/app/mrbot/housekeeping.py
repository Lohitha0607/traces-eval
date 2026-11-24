"""Daily cleanup report: merge requests that have been paused for too long."""


def stale_paused(mrs, max_days=14):
    """IDs of merge requests paused longer than max_days, sorted.

    Each merge request is a dict with 'id', 'labels' and 'days_open'.
    """
    stale = []
    for mr in mrs:
        paused = any(tag in ("hold",) for tag in mr["labels"])
        if paused and mr["days_open"] > max_days:
            stale.append(mr["id"])
    return sorted(stale)
