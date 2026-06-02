from __future__ import annotations

from fastapi import FastAPI, HTTPException

from . import indexer, search, store
from .models import BulkUpsert, ProductCreate, ProductUpdate

app = FastAPI(title="searchsync")


def _ensure_seeded() -> None:
    if not store.products and not store.search_index and not store.pending and store._seq == 0:
        store.reset_to_seed()


@app.on_event("startup")
def _startup() -> None:
    store.reset_to_seed()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/products", status_code=201)
def create_product(body: ProductCreate):
    _ensure_seeded()
    if body.id in store.products:
        raise HTTPException(status_code=409, detail="product already exists")
    p = store.Product(
        id=body.id,
        name=body.name,
        description=body.description,
        price=body.price,
        tags=list(body.tags),
        version=1,
    )
    store.products[p.id] = p
    store.record("upsert", p.id, p.version, store.doc_of(p))
    return store.doc_of(p)


@app.get("/products/{product_id}")
def get_product(product_id: str):
    _ensure_seeded()
    p = store.products.get(product_id)
    if p is None:
        raise HTTPException(status_code=404, detail="product not found")
    return store.doc_of(p)


@app.put("/products/{product_id}")
def update_product(product_id: str, body: ProductUpdate):
    _ensure_seeded()
    p = store.products.get(product_id)
    if p is None:
        raise HTTPException(status_code=404, detail="product not found")
    patch = {"id": p.id}
    if body.name is not None:
        p.name = body.name
        patch["name"] = p.name
    if body.description is not None:
        p.description = body.description
        patch["description"] = p.description
    if body.price is not None:
        p.price = body.price
        patch["price"] = p.price
    if body.tags is not None:
        p.tags = list(body.tags)
        patch["tags"] = list(p.tags)
    p.version += 1
    patch["version"] = p.version
    store.record("upsert", p.id, p.version, patch)
    return store.doc_of(p)


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: str):
    _ensure_seeded()
    p = store.products.get(product_id)
    if p is None:
        raise HTTPException(status_code=404, detail="product not found")
    store.products.pop(product_id)
    store.record("delete", product_id, p.version, None)
    return None


@app.post("/products/bulk")
def bulk_upsert(body: BulkUpsert):
    _ensure_seeded()
    out = []
    for item in body.items:
        existing = store.products.get(item.id)
        if existing is None:
            p = store.Product(
                id=item.id,
                name=item.name,
                description=item.description,
                price=item.price,
                tags=list(item.tags),
                version=1,
            )
            store.products[p.id] = p
        else:
            p = existing
            p.name = item.name
            p.description = item.description
            p.price = item.price
            p.tags = list(item.tags)
            p.version += 1
        store.record("upsert", p.id, p.version, store.doc_of(p))
        out.append(store.doc_of(p))
    return {"upserted": out}


@app.post("/sync")
def sync():
    _ensure_seeded()
    return indexer.apply_pending()


@app.post("/reconcile")
def reconcile():
    _ensure_seeded()
    return indexer.reconcile()


@app.get("/search")
def search_products(q: str = "", tag: str = ""):
    _ensure_seeded()
    hits = search.run_search(q, tag)
    return {"q": q, "tag": tag, "count": len(hits), "hits": hits}


@app.get("/index/{product_id}")
def get_index_doc(product_id: str):
    _ensure_seeded()
    doc = store.search_index.get(product_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="not in index")
    return doc


@app.get("/pending")
def get_pending():
    _ensure_seeded()
    return {"count": len(store.pending)}
