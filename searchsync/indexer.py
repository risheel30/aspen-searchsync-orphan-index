from __future__ import annotations

from . import store
from .coalesce import coalesce


def apply_pending() -> dict:
    plan = coalesce(store.pending)
    applied = 0
    for ev in plan:
        if ev.op == "delete":
            store.search_index.pop(ev.product_id, None)
        else:
            store.search_index[ev.product_id] = ev.doc
        applied += 1
    store.pending.clear()
    return {"applied": applied, "index_size": len(store.search_index)}


def reconcile() -> dict:
    reindexed = 0
    for pid, product in store.products.items():
        store.search_index[pid] = store.doc_of(product)
        reindexed += 1
    return {"reindexed": reindexed, "index_size": len(store.search_index)}
