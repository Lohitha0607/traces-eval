from stats import summarize


def test_old_format():
    assert summarize("data/old_runner_stats.json") == {"tests": 3, "failures": 3, "tries": 10}
