import pytest
from tests.factories.categories import CategoryFactory


@pytest.mark.asyncio
async def test_get_categories_list_success(async_client, mock_uow, patch_uow):
    fake_models = CategoryFactory.build_batch(3)
    uow = mock_uow({"categories": {"all": fake_models}})

    async with patch_uow(uow):
        response = await async_client.get("/api/v1/categories")

    assert response.status_code == 200
    payload = response.json()
    assert "data" in payload
    assert len(payload["data"]) == 3
    uow.categories.all.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_categories_list_by_slugs_success(async_client, mock_uow, patch_uow):
    fake_models = [
        CategoryFactory.build(id=1, name="Category One", slug="category-one"),
        CategoryFactory.build(id=2, name="Category Two", slug="category-two"),
    ]
    uow = mock_uow({"categories": {"get_category_names_from_slugs": fake_models}})

    async with patch_uow(uow):
        response = await async_client.get(
            "/api/v1/categories/by-slugs?slugs=category-one&slugs=category-two",
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"] == [
        ["Category One", "category-one"],
        ["Category Two", "category-two"],
    ]
    uow.categories.get_category_names_from_slugs.assert_awaited_once_with(
        slugs=["category-one", "category-two"],
    )


@pytest.mark.asyncio
async def test_get_child_categories_success(async_client, mock_uow, patch_uow):
    fake_models = [
        CategoryFactory.build(id=10, parent_id=1),
        CategoryFactory.build(id=11, parent_id=2),
    ]
    uow = mock_uow({"categories": {"get_children_by_parent_ids": fake_models}})

    async with patch_uow(uow):
        response = await async_client.get(
            "/api/v1/categories/children?parent_ids=1&parent_ids=2",
        )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["data"]) == 2
    uow.categories.get_children_by_parent_ids.assert_awaited_once_with([1, 2])


@pytest.mark.asyncio
async def test_create_category_success(
    async_client, mock_uow, patch_uow, patch_superuser,
):
    category_in = {"name": "Some category", "slug": "some-category"}
    fake_model = CategoryFactory.build(
        id=1, name=category_in["name"], slug=category_in["slug"],
    )
    uow = mock_uow({"categories": {"exists": False, "create": fake_model}})

    async with patch_uow(uow), patch_superuser():
        response = await async_client.post("/api/v1/categories", json=category_in)

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["id"] == 1
    assert payload["data"]["name"] == category_in["name"]
    assert payload["data"]["slug"] == category_in["slug"]
    uow.categories.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_category_conflict_slug_exists(
    async_client, mock_uow, patch_uow, patch_superuser,
):
    category_in = {"name": "Some category", "slug": "some-category"}
    uow = mock_uow({"categories": {"exists": True, "create": None}})

    async with patch_uow(uow), patch_superuser():
        response = await async_client.post("/api/v1/categories", json=category_in)

    assert response.status_code == 409
    payload = response.json()
    assert payload["data"] is None
    assert payload["errors"][0]["code"] == "unique_conflict"
    assert "slug" in payload["errors"][0]["meta"]


@pytest.mark.asyncio
async def test_create_category_conflict_parent_not_found(
    async_client, mock_uow, patch_uow, patch_superuser,
):
    category_in = {
        "name": "Child category",
        "slug": "child-category",
        "parent_id": 999,
    }
    uow = mock_uow({"categories": {"exists": False, "create": None}})

    async def exists_side_effect(**kwargs):
        if kwargs.get("slug") == "child-category":
            return False
        if kwargs.get("id") == 999:
            return False
        return False

    uow.categories.exists.side_effect = exists_side_effect

    async with patch_uow(uow), patch_superuser():
        response = await async_client.post("/api/v1/categories", json=category_in)

    assert response.status_code == 400
    payload = response.json()
    assert payload["data"] is None
    assert payload["errors"][0]["code"] == "foreign_key_violation"


@pytest.mark.asyncio
async def test_create_category_validation_error_invalid_slug(
    async_client, mock_uow, patch_uow, patch_superuser,
):
    uow = mock_uow({"categories": {"exists": False, "create": None}})
    async with patch_uow(uow), patch_superuser():
        response = await async_client.post(
            "/api/v1/categories",
            json={"name": "Some category", "slug": "Bad_Slug"},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_category_success(
    async_client, mock_uow, patch_uow, patch_superuser,
):
    category_in = {"name": "Updated category"}
    fake_model = CategoryFactory.build(
        id=1, name="Updated category", slug="some-category",
    )
    uow = mock_uow({"categories": {"update": fake_model}})

    async with patch_uow(uow), patch_superuser():
        response = await async_client.patch("/api/v1/categories/1", json=category_in)

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["id"] == 1
    assert payload["data"]["name"] == "Updated category"
    uow.categories.update.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_category_conflict_slug_exists(
    async_client, mock_uow, patch_uow, patch_superuser,
):
    category_in = {"slug": "some-category"}
    uow = mock_uow({"categories": {"exists": True, "update": None}})

    async with patch_uow(uow), patch_superuser():
        response = await async_client.patch("/api/v1/categories/1", json=category_in)

    assert response.status_code == 409
    payload = response.json()
    assert payload["data"] is None
    assert payload["errors"][0]["code"] == "unique_conflict"
    assert "slug" in payload["errors"][0]["meta"]


@pytest.mark.asyncio
async def test_delete_category_success(
    async_client, mock_uow, patch_uow, patch_superuser,
):
    uow = mock_uow({"categories": {"delete": None}})
    async with patch_uow(uow), patch_superuser():
        response = await async_client.delete("/api/v1/categories/1")

    assert response.status_code == 200
    assert response.content in (b"", b"null")
    uow.categories.delete.assert_awaited_once_with(id=1)
