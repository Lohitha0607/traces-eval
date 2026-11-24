from shop.catalog import Catalog


def make():
    c = Catalog()
    c.add("A1", "Desk lamp", "warm light")
    c.add("A2", "Desk chair", "ergonomic")
    return c


def test_suggest():
    assert make().suggest("desk") == ["Desk chair", "Desk lamp"]


def test_search():
    assert make().search("warm") == ["Desk lamp"]
