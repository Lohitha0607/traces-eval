from catalog import Catalog


def test_list_items_prefix():
    c = Catalog()
    c.add("apple"); c.add("apricot"); c.add("banana")
    assert c.list_items("ap") == ["apple", "apricot"]


def test_search_description():
    c = Catalog()
    c.add("tool", "a handy hammer")
    assert c.search("HAMMER") == ["tool"]
