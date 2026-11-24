"""Summarise test-runner statistics.

Old runner format: {test_name: [failures, tries]}.
"""

import json


def count_failures(stats):
    """Total number of failures across all tests."""
    total = 0
    for failures, tries in stats.values():
        total += failures
    return total


def summarize(path):
    """Return {'tests': n, 'failures': f, 'tries': t} for a stats JSON file."""
    with open(path) as f:
        stats = json.load(f)
    tries = sum(record[1] for record in stats.values())
    return {"tests": len(stats), "failures": count_failures(stats), "tries": tries}
