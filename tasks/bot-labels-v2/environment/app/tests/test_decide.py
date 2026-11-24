from mrbot.decide import decide


def test_wait():
    assert decide([]) == "wait"


def test_hold_wins():
    assert decide(["lgtm", "blocked"]) == "hold"
