from mrbot.approve import add_approval
from mrbot.decide import decide
from mrbot.housekeeping import stale_paused
from mrbot.notify import ready_message


def test_decide_new_and_old():
    assert decide(["bot/approved"]) == "merge"
    assert decide(["bot/automerge"]) == "merge"
    assert decide(["bot/hold", "bot/approved"]) == "hold"
    assert decide(["approved"]) == "merge"
    assert decide(["hold", "approved"]) == "hold"
    assert decide(["blocked", "bot/approved"]) == "hold"


def test_add_approval_prefixed_once():
    mr = {"labels": ["lgtm"]}
    add_approval(mr); add_approval(mr)
    assert mr["labels"].count("bot/approved") == 1 and "approved" not in mr["labels"]


def test_housekeeping_new_and_old():
    mrs = [{"id": 1, "labels": ["bot/hold"], "days_open": 30},
           {"id": 2, "labels": ["hold"], "days_open": 30},
           {"id": 3, "labels": ["bot/hold"], "days_open": 2},
           {"id": 4, "labels": ["lgtm"], "days_open": 99}]
    assert stale_paused(mrs) == [1, 2]


def test_notify_new_and_old():
    assert ready_message({"id": 7, "labels": ["bot/approved"]}) == "MR !7 is ready to merge"
    assert ready_message({"id": 8, "labels": ["approved"]}) == "MR !8 is ready to merge"
    assert ready_message({"id": 9, "labels": ["lgtm"]}) is None
