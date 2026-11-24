from mergebot import decide


def test_wait_without_labels():
    assert decide([]) == "wait"


def test_hold_wins():
    assert decide(["lgtm", "blocked"]) == "hold"
