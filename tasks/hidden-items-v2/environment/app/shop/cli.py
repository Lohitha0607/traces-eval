"""Tiny command line front end."""
import sys

from shop.catalog import Catalog


def main(argv=None):
    argv = argv or sys.argv[1:]
    catalog = Catalog()
    catalog.add("A1", "Desk lamp", "warm light")
    if argv and argv[0] == "search":
        print("\n".join(catalog.search(" ".join(argv[1:]))))


if __name__ == "__main__":
    main()
