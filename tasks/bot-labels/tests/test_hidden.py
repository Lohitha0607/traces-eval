from mergebot import add_approval, decide


def test_new_labels():
    assert decide(["bot/approved"]) == "merge"
    assert decide(["bot/automerge"]) == "merge"
    assert decide(["bot/hold", "bot/approved"]) == "hold"


def test_old_labels_still_work():
    assert decide(["approved"]) == "merge"
    assert decide(["automerge"]) == "merge"
    assert decide(["hold", "approved"]) == "hold"


def test_unchanged_labels():
    assert decide(["lgtm"]) == "merge"
    assert decide(["blocked", "bot/approved"]) == "hold"
    assert decide([]) == "wait"


def test_add_approval_uses_prefix_once():
    mr = {"labels": ["lgtm"]}
    add_approval(mr); add_approval(mr)
    assert mr["labels"].count("bot/approved") == 1
    assert "approved" not in mr["labels"]
