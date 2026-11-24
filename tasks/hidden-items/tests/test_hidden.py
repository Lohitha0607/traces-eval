from catalog import Catalog


def make():
    c = Catalog()
    c.add("alpha", "first letter")
    c.add("alpine", "mountain", hidden=True)
    c.add("beta", "second letter about alpine skiing")
    return c


def test_list_items_skips_hidden():
    assert make().list_items("al") == ["alpha"]


def test_search_skips_hidden():
    assert make().search("alpine") == ["beta"]


def test_get_still_returns_hidden():
    assert make().get("alpine").hidden is True


def test_visible_behaviour_unchanged():
    c = make()
    assert c.list_items() == ["alpha", "beta"]
    assert c.search("LETTER") == ["alpha", "beta"]
