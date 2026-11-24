import json

from stats import count_failures, summarize


def test_old_format_unchanged():
    assert summarize("data/old_runner_stats.json") == {"tests": 3, "failures": 3, "tries": 10}


def test_new_format_summary():
    assert summarize("data/new_runner_stats.json") == {"tests": 4, "failures": 5, "tries": 13}


def test_new_format_count_failures():
    stats = json.load(open("data/new_runner_stats.json"))
    assert count_failures(stats) == 5


def test_other_new_file():
    stats = {"_format": ["tries", "failures", "skips"], "a": [10, 4, 0], "b": [1, 0, 1]}
    assert count_failures(stats) == 4
