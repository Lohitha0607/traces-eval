"""Decides what to do with a merge request from its labels."""

MERGE_LABELS = ["approved", "automerge", "lgtm"]
HOLD_LABELS = ["hold", "blocked"]


def decide(labels):
    """Return 'hold', 'merge' or 'wait' for a merge request with these labels."""
    labels = set(labels)
    if labels & set(HOLD_LABELS):
        return "hold"
    if labels & set(MERGE_LABELS):
        return "merge"
    return "wait"


def add_approval(mr):
    """Mark a merge request (a dict with a 'labels' list) as approved by the bot."""
    if "approved" not in mr["labels"]:
        mr["labels"].append("approved")
    return mr
