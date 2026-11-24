"""Decide what to do with a merge request."""
from mrbot import labels


def decide(mr_labels):
    """Return 'hold', 'merge' or 'wait'."""
    current = set(mr_labels)
    if current & set(labels.HOLD_LABELS):
        return "hold"
    if current & set(labels.MERGE_LABELS):
        return "merge"
    return "wait"
