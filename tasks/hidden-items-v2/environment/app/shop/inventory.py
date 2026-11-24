"""Stock levels per SKU."""


class Inventory:
    def __init__(self):
        self._stock = {}

    def set(self, sku, count):
        self._stock[sku] = count

    def in_stock(self, sku):
        return self._stock.get(sku, 0) > 0
