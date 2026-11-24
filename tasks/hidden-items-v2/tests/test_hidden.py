from shop.catalog import Catalog


def make():
    c = Catalog()
    c.add("A1", "Desk lamp", "warm light")
    c.add("A2", "Desk chair", "ergonomic")
    c.add("S1", "Desk prototype", "warm secret model", flags={"unlisted"})
    return c


def test_suggest_hides_unlisted():
    assert make().suggest("desk") == ["Desk chair", "Desk lamp"]


def test_search_hides_unlisted():
    assert make().search("warm") == ["Desk lamp"]
    assert make().search("prototype") == []


def test_get_still_works():
    assert make().get("S1").name == "Desk prototype"


def test_listed_unchanged():
    c = make()
    assert c.search("desk") == ["Desk chair", "Desk lamp"]
