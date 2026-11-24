import json

from ci_report.flaky import flaky_tests
from ci_report.load import load_stats
from ci_report.summary import summarize


def test_summary_old():
    assert summarize("data/old_runner_stats.json") == {"tests": 3, "failures": 5, "tries": 10}


def test_summary_new():
    assert summarize("data/new_runner_stats.json") == {"tests": 4, "failures": 5, "tries": 13}


def test_flaky_old():
    assert flaky_tests(load_stats("data/old_runner_stats.json")) == ["test_logout"]


def test_flaky_new():
    assert flaky_tests(load_stats("data/new_runner_stats.json")) == ["test_logout", "test_upload"]


def test_other_new_file(tmp_path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"runner_version": 2, "tests": {"a": [10, 4, 0], "b": [1, 0, 1]}}))
    assert summarize(str(p)) == {"tests": 2, "failures": 4, "tries": 11}
