"""The catalog: add products, fetch them, suggest names and search."""
from shop.models import Product
from shop.search.index import SearchIndex


class Catalog:
    def __init__(self):
        self._products = {}
        self._index = SearchIndex()

    def add(self, sku, name, description="", price_cents=0, flags=()):
        product = Product(sku, name, description, price_cents, set(flags))
        self._products[sku] = product
        self._index.add(sku, f"{name} {description}")
        return product

    def get(self, sku):
        return self._products[sku]

    def suggest(self, prefix):
        """Product names starting with prefix (case-insensitive), sorted. Used for autocompletion."""
        p = prefix.lower()
        return sorted(pr.name for pr in self._products.values() if pr.name.lower().startswith(p))

    def search(self, query):
        """Names of products matching every word of the query, sorted."""
        skus = self._index.query(query)
        return sorted(self._products[s].name for s in skus)
