# from unittest.mock import AsyncMock

# import pytest
# from tests.factories.categories import CategoryFactory

# from app.services.files import AbstractFileStorageService, LocalFileStorage


# @pytest.mark.asyncio
# async def test_get_categories_list_success(async_client, mock_uow, patch_uow):
#     fake_models = CategoryFactory.build_batch(3)
#     uow = mock_uow({"categories": {"all": fake_models}})

#     async with patch_uow(uow):
#         response = await async_client.get("/api/v1/categories")

#     assert response.status_code == 200
#     payload = response.json()
#     assert "data" in payload
#     assert len(payload["data"]) == 3
#     uow.categories.all.assert_awaited_once()


# @pytest.mark.asyncio
# async def test_get_categories_list_by_slugs_success(async_client, mock_uow, patch_uow):
#     fake_models = [
#         CategoryFactory.build(id=1, name="Category One", slug="category-one"),
#         CategoryFactory.build(id=2, name="Category Two", slug="category-two"),
#     ]
#     uow = mock_uow({"categories": {"get_category_names_from_slugs": fake_models}})

#     async with patch_uow(uow):
#         response = await async_client.get(
#             "/api/v1/categories/by-slugs?slugs=category-one&slugs=category-two",
#         )

#     assert response.status_code == 200
#     payload = response.json()
#     assert payload["data"] == [
#         ["Category One", "category-one"],
#         ["Category Two", "category-two"],
#     ]
#     uow.categories.get_category_names_from_slugs.assert_awaited_once_with(
#         slugs=["category-one", "category-two"],
#     )


# @pytest.mark.asyncio
# async def test_get_child_categories_success(async_client, mock_uow, patch_uow):
#     fake_models = [
#         CategoryFactory.build(id=10, parent_id=1),
#         CategoryFactory.build(id=11, parent_id=2),
#     ]
#     uow = mock_uow({"categories": {"get_children_by_parent_ids": fake_models}})

#     async with patch_uow(uow):
#         response = await async_client.get(
#             "/api/v1/categories/children?parent_ids=1&parent_ids=2",
#         )

#     assert response.status_code == 200
#     payload = response.json()
#     assert len(payload["data"]) == 2
#     uow.categories.get_children_by_parent_ids.assert_awaited_once_with([1, 2])


# # ==================== Create ====================


# @pytest.mark.asyncio
# async def test_create_category_success(
#     async_client, mock_uow, patch_uow, patch_superuser,
# ):
#     fake_model = CategoryFactory.build(id=1, name="Some category", slug="some-category")
#     uow = mock_uow({"categories": {"exists": False, "create": fake_model}})

#     async with patch_uow(uow), patch_superuser():
#         response = await async_client.post(
#             "/api/v1/categories",
#             data={"name": "Some category", "slug": "some-category"},
#         )

#     assert response.status_code == 200
#     payload = response.json()
#     assert payload["data"]["id"] == 1
#     assert payload["data"]["name"] == "Some category"
#     assert payload["data"]["slug"] == "some-category"
#     uow.categories.create.assert_awaited_once()


# @pytest.mark.asyncio
# async def test_create_category_with_image_success(
#     async_client, mock_uow, patch_uow, patch_superuser, monkeypatch,
# ):
#     monkeypatch.setattr(AbstractFileStorageService, "verify_file", AsyncMock(return_value=True))
#     monkeypatch.setattr(LocalFileStorage, "upload", AsyncMock(return_value=None))
#     # monkeypatch.setattr(SupabaseFileStorage, "upload", AsyncMock(return_value=None))

#     fake_model = CategoryFactory.build(
#         id=1, name="Some category", slug="some-category", file_path="uploads/categories/some-category/img.jpg",
#     )
#     uow = mock_uow({"categories": {"exists": False, "create": fake_model}})

#     async with patch_uow(uow), patch_superuser():
#         response = await async_client.post(
#             "/api/v1/categories",
#             data={"name": "Some category", "slug": "some-category"},
#             files=[("image", ("img.jpg", b"fake-bytes", "image/jpeg"))],
#         )

#     assert response.status_code == 200
#     payload = response.json()
#     assert payload["data"]["file_path"] is not None
#     assert "categories/some-category" in payload["data"]["file_path"]


# @pytest.mark.asyncio
# async def test_create_category_with_parent_success(
#     async_client, mock_uow, patch_uow, patch_superuser,
# ):
#     fake_model = CategoryFactory.build(id=2, name="Child category", slug="child-category", parent_id=1)

#     async def exists_side_effect(**kwargs):
#         if "slug" in kwargs:
#             return False
#         if "id" in kwargs:
#             return True
#         return False

#     uow = mock_uow({"categories": {"exists": None, "create": fake_model}})
#     uow.categories.exists = AsyncMock(side_effect=exists_side_effect)

#     async with patch_uow(uow), patch_superuser():
#         response = await async_client.post(
#             "/api/v1/categories",
#             data={"name": "Child category", "slug": "child-category", "parent_id": "1"},
#         )

#     assert response.status_code == 200
#     payload = response.json()
#     assert payload["data"]["parent_id"] == 1


# @pytest.mark.asyncio
# async def test_create_category_conflict_slug_exists(
#     async_client, mock_uow, patch_uow, patch_superuser,
# ):
#     uow = mock_uow({"categories": {"exists": True, "create": None}})

#     async with patch_uow(uow), patch_superuser():
#         response = await async_client.post(
#             "/api/v1/categories",
#             data={"name": "Some category", "slug": "some-category"},
#         )

#     assert response.status_code == 409
#     payload = response.json()
#     assert payload["data"] is None
#     assert payload["errors"][0]["code"] == "unique_conflict"
#     assert "slug" in payload["errors"][0]["meta"]


# @pytest.mark.asyncio
# async def test_create_category_conflict_slug_exists_cleans_up_image(
#     async_client, mock_uow, patch_uow, patch_superuser, monkeypatch,
# ):
#     monkeypatch.setattr(AbstractFileStorageService, "verify_file", AsyncMock(return_value=True))
#     monkeypatch.setattr(LocalFileStorage, "upload", AsyncMock(return_value=None))
#     mock_cleanup = AsyncMock(return_value=None)
#     monkeypatch.setattr(LocalFileStorage, "cleanup_files", mock_cleanup)
#     # monkeypatch.setattr(SupabaseFileStorage, "upload", AsyncMock(return_value=None))
#     # monkeypatch.setattr(SupabaseFileStorage, "cleanup_files", AsyncMock(return_value=None))

#     uow = mock_uow({"categories": {"exists": True, "create": None}})

#     async with patch_uow(uow), patch_superuser():
#         response = await async_client.post(
#             "/api/v1/categories",
#             data={"name": "Some category", "slug": "some-category"},
#             files=[("image", ("img.jpg", b"fake-bytes", "image/jpeg"))],
#         )

#     assert response.status_code == 409
#     mock_cleanup.assert_awaited_once()


# @pytest.mark.asyncio
# async def test_create_category_conflict_parent_not_found(
#     async_client, mock_uow, patch_uow, patch_superuser,
# ):
#     async def exists_side_effect(**kwargs):
#         if "slug" in kwargs:
#             return False
#         if "id" in kwargs:
#             return False
#         return False

#     uow = mock_uow({"categories": {"exists": None, "create": None}})
#     uow.categories.exists = AsyncMock(side_effect=exists_side_effect)

#     async with patch_uow(uow), patch_superuser():
#         response = await async_client.post(
#             "/api/v1/categories",
#             data={"name": "Child category", "slug": "child-category", "parent_id": "999"},
#         )

#     assert response.status_code == 400
#     payload = response.json()
#     assert payload["errors"][0]["code"] == "foreign_key_violation"


# @pytest.mark.asyncio
# async def test_create_category_unauthorized(async_client):
#     response = await async_client.post(
#         "/api/v1/categories",
#         data={"name": "Some category", "slug": "some-category"},
#     )
#     assert response.status_code == 401


# # ==================== Update ====================


# @pytest.mark.asyncio
# async def test_update_category_success(
#     async_client, mock_uow, patch_uow, patch_superuser,
# ):
#     fake_model = CategoryFactory.build(id=1, name="Updated category", slug="some-category")
#     uow = mock_uow({"categories": {"get_or_none": None, "update": fake_model}})

#     async with patch_uow(uow), patch_superuser():
#         response = await async_client.patch(
#             "/api/v1/categories/1",
#             data={"name": "Updated category"},
#         )

#     assert response.status_code == 200
#     payload = response.json()
#     assert payload["data"]["name"] == "Updated category"
#     uow.categories.update.assert_awaited_once()


# @pytest.mark.asyncio
# async def test_update_category_with_image_success(
#     async_client, mock_uow, patch_uow, patch_superuser, monkeypatch,
# ):
#     monkeypatch.setattr(AbstractFileStorageService, "verify_file", AsyncMock(return_value=True))
#     monkeypatch.setattr(LocalFileStorage, "upload", AsyncMock(return_value=None))
#     monkeypatch.setattr(SupabaseFileStorage, "upload", AsyncMock(return_value=None))

#     current = CategoryFactory.build(id=1, name="Category", slug="some-category")
#     updated = CategoryFactory.build(
#         id=1, name="Category", slug="some-category", file_path="uploads/categories/some-category/new.jpg",
#     )
#     uow = mock_uow({"categories": {"get": current, "get_or_none": None, "update": updated}})

#     async with patch_uow(uow), patch_superuser():
#         response = await async_client.patch(
#             "/api/v1/categories/1",
#             data={"name": "Category", "slug": "some-category"},
#             files=[("image", ("new.jpg", b"fake-bytes", "image/jpeg"))],
#         )

#     assert response.status_code == 200
#     payload = response.json()
#     assert payload["data"]["file_path"] is not None


# @pytest.mark.asyncio
# async def test_update_category_slug_conflict(
#     async_client, mock_uow, patch_uow, patch_superuser,
# ):
#     other = CategoryFactory.build(id=2, slug="taken-slug")
#     uow = mock_uow({"categories": {"get_or_none": other, "update": None}})

#     async with patch_uow(uow), patch_superuser():
#         response = await async_client.patch(
#             "/api/v1/categories/1",
#             data={"slug": "taken-slug"},
#         )

#     assert response.status_code == 409
#     payload = response.json()
#     assert "slug" in payload["errors"][0]["meta"]


# @pytest.mark.asyncio
# async def test_update_category_same_slug_no_conflict(
#     async_client, mock_uow, patch_uow, patch_superuser,
# ):
#     same = CategoryFactory.build(id=1, slug="same-slug")
#     updated = CategoryFactory.build(id=1, name="Updated", slug="same-slug")
#     uow = mock_uow({"categories": {"get_or_none": same, "update": updated}})

#     async with patch_uow(uow), patch_superuser():
#         response = await async_client.patch(
#             "/api/v1/categories/1",
#             data={"name": "Updated", "slug": "same-slug"},
#         )

#     assert response.status_code == 200


# # ==================== Delete ====================


# @pytest.mark.asyncio
# async def test_delete_category_success(
#     async_client, mock_uow, patch_uow, patch_superuser,
# ):
#     uow = mock_uow({"categories": {"delete": None}})
#     async with patch_uow(uow), patch_superuser():
#         response = await async_client.delete("/api/v1/categories/1")

#     assert response.status_code == 200
#     assert response.content in (b"", b"null")
#     uow.categories.delete.assert_awaited_once_with(id=1)


# @pytest.mark.asyncio
# async def test_delete_category_unauthorized(async_client):
#     response = await async_client.delete("/api/v1/categories/1")
#     assert response.status_code == 401
