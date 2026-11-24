"""Prices and discounts (unrelated to listing)."""


def apply_discount(price_cents, percent):
    return round(price_cents * (100 - percent) / 100)


def format_price(price_cents):
    return f"${price_cents / 100:.2f}"
