"""End-to-end tests against the FastAPI app via httpx.AsyncClient."""

import pytest


async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


async def test_list_empty(client):
    r = await client.get("/items")
    assert r.status_code == 200
    body = r.json()
    assert body == {"items": [], "total": 0, "limit": 50, "offset": 0}


async def test_create_then_get(client):
    r = await client.post("/items", json={"name": "first", "description": "hello"})
    assert r.status_code == 201
    item = r.json()
    assert item["name"] == "first"
    assert item["description"] == "hello"
    item_id = item["id"]

    r2 = await client.get(f"/items/{item_id}")
    assert r2.status_code == 200
    assert r2.json()["name"] == "first"


async def test_create_validation_error(client):
    r = await client.post("/items", json={"name": ""})
    assert r.status_code == 422


async def test_patch_partial_update(client):
    r = await client.post("/items", json={"name": "first"})
    item_id = r.json()["id"]

    r2 = await client.patch(f"/items/{item_id}", json={"description": "added later"})
    assert r2.status_code == 200
    assert r2.json()["description"] == "added later"
    assert r2.json()["name"] == "first"


async def test_delete_then_404(client):
    r = await client.post("/items", json={"name": "doomed"})
    item_id = r.json()["id"]

    r2 = await client.delete(f"/items/{item_id}")
    assert r2.status_code == 204

    r3 = await client.get(f"/items/{item_id}")
    assert r3.status_code == 404


async def test_pagination(client):
    for i in range(5):
        await client.post("/items", json={"name": f"item-{i}"})

    r = await client.get("/items?limit=2&offset=0")
    body = r.json()
    assert body["total"] == 5
    assert len(body["items"]) == 2
    assert body["items"][0]["name"] == "item-0"

    r2 = await client.get("/items?limit=2&offset=2")
    body2 = r2.json()
    assert len(body2["items"]) == 2
    assert body2["items"][0]["name"] == "item-2"


async def test_invalid_pagination(client):
    r = await client.get("/items?limit=0")
    assert r.status_code == 422


@pytest.mark.parametrize("missing_id", [99999, 0, -1])
async def test_get_missing(client, missing_id: int):
    r = await client.get(f"/items/{missing_id}")
    assert r.status_code in (404, 422)
