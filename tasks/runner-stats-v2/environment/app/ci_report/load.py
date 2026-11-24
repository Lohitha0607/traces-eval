"""Load a stats file written by the test runner."""
import json


def load_stats(path):
    with open(path) as f:
        return json.load(f)


def records(stats):
    """Yield (name, failures, tries) for every test."""
    for name, (failures, tries) in stats.items():
        yield name, failures, tries
