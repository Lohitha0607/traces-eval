"""Actions the bot performs on merge requests."""
from mrbot import labels


def add_approval(mr):
    """Mark a merge request (a dict with a 'labels' list) as approved by the bot."""
    if labels.APPROVED not in mr["labels"]:
        mr["labels"].append(labels.APPROVED)
    return mr
