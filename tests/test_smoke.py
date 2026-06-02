def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_seeded_product_is_searchable(client):
    r = client.get("/search", params={"q": "office"})
    assert r.status_code == 200
    ids = {h["id"] for h in r.json()["hits"]}
    assert "p-2" in ids


def test_create_then_sync_finds_it(client):
    client.post("/products", json={"id": "p-9", "name": "Solis Keyboard", "description": "low profile", "price": 80.0, "tags": ["desk"]})
    client.post("/sync")
    r = client.get("/search", params={"q": "solis"})
    assert r.json()["count"] == 1
    assert r.json()["hits"][0]["id"] == "p-9"


def test_detail_returns_product(client):
    r = client.get("/products/p-1")
    assert r.status_code == 200
    assert r.json()["name"] == "Aurora Desk Lamp"


def test_update_name_reflected_in_search_after_sync(client):
    client.put("/products/p-1", json={"name": "Aurora Pro Lamp"})
    client.post("/sync")
    r = client.get("/search", params={"q": "aurora pro"})
    assert r.json()["count"] == 1
    assert r.json()["hits"][0]["name"] == "Aurora Pro Lamp"


def test_delete_then_sync_removes_from_search(client):
    client.delete("/products/p-3")
    client.post("/sync")
    r = client.get("/search", params={"q": "cobalt"})
    assert r.json()["count"] == 0
    detail = client.get("/products/p-3")
    assert detail.status_code == 404


def test_bulk_upsert_then_sync(client):
    client.post("/products/bulk", json={"items": [
        {"id": "p-10", "name": "Vesta Mug", "description": "ceramic", "price": 12.0, "tags": ["kitchen"]},
        {"id": "p-11", "name": "Orbit Mousepad", "description": "felt", "price": 15.0, "tags": ["desk"]},
    ]})
    client.post("/sync")
    r = client.get("/search", params={"q": "vesta"})
    assert r.json()["count"] == 1
