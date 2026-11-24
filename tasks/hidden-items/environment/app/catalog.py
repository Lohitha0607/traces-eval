"""A tiny catalog of named items with prefix suggestions and search."""

from dataclasses import dataclass


@dataclass
class Item:
    name: str
    description: str = ""
    hidden: bool = False


class Catalog:
    def __init__(self):
        self._items = {}

    def add(self, name, description="", hidden=False):
        self._items[name] = Item(name, description, hidden)

    def get(self, name):
        return self._items[name]

    def list_items(self, prefix=""):
        """Names starting with prefix, sorted (used for autocompletion)."""
        return sorted(n for n in self._items if n.startswith(prefix))

    def search(self, query):
        """Names whose name or description contains query (case-insensitive), sorted."""
        q = query.lower()
        return sorted(n for n, it in self._items.items() if q in n.lower() or q in it.description.lower())
