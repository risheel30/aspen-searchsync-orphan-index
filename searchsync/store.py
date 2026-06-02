from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Product:
    id: str
    name: str
    description: str = ""
    price: float = 0.0
    tags: List[str] = field(default_factory=list)
    version: int = 1


@dataclass
class Event:
    seq: int
    op: str
    product_id: str
    version: int
    doc: Optional[dict] = None


products: Dict[str, Product] = {}
search_index: Dict[str, dict] = {}
pending: List[Event] = []

_seq = 0


def next_seq() -> int:
    global _seq
    _seq += 1
    return _seq


def doc_of(p: Product) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": p.price,
        "tags": list(p.tags),
        "version": p.version,
    }


def record(op: str, product_id: str, version: int, doc: Optional[dict] = None) -> None:
    pending.append(Event(next_seq(), op, product_id, version, doc))


SEED_PRODUCTS = [
    Product(id="p-1", name="Aurora Desk Lamp", description="Warm LED desk lamp", price=39.0, tags=["lighting", "office"]),
    Product(id="p-2", name="Nimbus Office Chair", description="Mesh-back ergonomic chair", price=210.0, tags=["furniture", "office"]),
    Product(id="p-3", name="Cobalt Water Bottle", description="Insulated steel bottle", price=24.0, tags=["kitchen"]),
    Product(id="p-4", name="Lumen Monitor Stand", description="Bamboo monitor riser", price=48.0, tags=["office", "desk"]),
]


def reset_to_seed() -> None:
    global _seq
    products.clear()
    search_index.clear()
    pending.clear()
    _seq = 0
    for base in SEED_PRODUCTS:
        p = Product(
            id=base.id,
            name=base.name,
            description=base.description,
            price=base.price,
            tags=list(base.tags),
            version=1,
        )
        products[p.id] = p
        search_index[p.id] = doc_of(p)
        next_seq()
