"""Product model. A product is unlisted when its flags contain "unlisted"."""
from dataclasses import dataclass, field


@dataclass
class Product:
    sku: str
    name: str
    description: str = ""
    price_cents: int = 0
    flags: set = field(default_factory=set)

    def is_listed(self) -> bool:
        return "unlisted" not in self.flags
