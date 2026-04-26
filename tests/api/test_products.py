import json
from unittest.mock import AsyncMock

import pytest
from tests.factories.categories import CategoryFactory
from tests.factories.products import (
    ProductFiltersRepoResultFactory,
    ProductImageFactory,
    ProductVariationFactory,
    UniqueProductFactory,
)

from app.models.website_settings import WebSiteSettings
from app.services.files import AbstractFileStorageService, LocalFileStorage, SupabaseFileStorage


_default_ws = WebSiteSettings(id=1, manufacturer_discount=0, seller_markup=0)


@pytest.mark.asyncio
async def test_get_products_list_success(async_client, mock_uow, patch_uow):
    unique = UniqueProductFactory.build(id=1, slug="u-1", name="Unique 1")
    image = ProductImageFactory.build(id=1, product_id=1, file_path="uploads/u-1/img.jpg", product=unique)
    unique.images = [image]
    variation = ProductVariationFactory.build(id=10, product_id=1, product=unique, price=100.0)

    uow = mock_uow(
        {
            "products": {
                "list_product_previews": [variation],
                "count": 1,
            },
            "website_settings": {"get_or_none": _default_ws},
        },
    )

    async with patch_uow(uow):
        response = await async_client.get("/api/v1/products")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["pagination"]["total"] == 1
    assert payload["items"][0]["id"] == 10
    assert payload["items"][0]["slug"] == "u-1"
    assert payload["items"][0]["preview"]["file_path"] == "uploads/u-1/img.jpg"


@pytest.mark.asyncio
async def test_get_products_list_with_text_search(async_client, mock_uow, patch_uow):
    unique = UniqueProductFactory.build(id=1, slug="truba", name="Труба одностінна")
    image = ProductImageFactory.build(id=1, product_id=1, file_path="uploads/truba/img.jpg", product=unique)
    unique.images = [image]
    variation = ProductVariationFactory.build(id=10, product_id=1, product=unique, price=100.0)

    uow = mock_uow(
        {
            "products": {
                "list_product_previews": [variation],
                "count": 1,
            },
            "website_settings": {"get_or_none": _default_ws},
        },
    )

    async with patch_uow(uow):
        response = await async_client.get("/api/v1/products?text=труба")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["pagination"]["total"] == 1
    assert payload["items"][0]["id"] == 10

    uow.products.list_product_previews.assert_awaited_once()
    call_kwargs = uow.products.list_product_previews.await_args.kwargs
    assert call_kwargs["filters"].text == "труба"


@pytest.mark.asyncio
async def test_get_products_by_ids_success(async_client, mock_uow, patch_uow):
    unique = UniqueProductFactory.build(id=1, slug="u-1", name="Unique 1")
    unique.images = [ProductImageFactory.build(id=1, product_id=1, file_path="uploads/u-1/img.jpg", product=unique)]

    variations = [
        ProductVariationFactory.build(id=10, product_id=1, product=unique, price=100.0),
        ProductVariationFactory.build(id=11, product_id=1, product=unique, price=120.0),
    ]

    uow = mock_uow(
        {
            "products": {
                "all": variations,
            },
            "website_settings": {"get_or_none": _default_ws},
        },
    )

    async with patch_uow(uow):
        response = await async_client.get("/api/v1/products/by-ids?product_ids=10&product_ids=11")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert len(payload) == 2
    assert {item["id"] for item in payload} == {10, 11}


@pytest.mark.asyncio
async def test_get_unique_product_list_success(async_client, mock_uow, patch_uow):
    unique = UniqueProductFactory.build(id=1, slug="u-1", name="Unique 1")
    unique.images = [ProductImageFactory.build(id=1, product_id=1, file_path="uploads/u-1/img.jpg", product=unique)]

    uow = mock_uow(
        {
            "unique_products": {
                "all": [unique],
                "count": 1,
            },
        },
    )

    async with patch_uow(uow):
        response = await async_client.get("/api/v1/products/unique")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["pagination"]["total"] == 1
    assert payload["items"][0]["id"] == 1
    assert payload["items"][0]["slug"] == "u-1"
    assert payload["items"][0]["images"][0]["file_path"] == "uploads/u-1/img.jpg"


@pytest.mark.asyncio
async def test_get_unique_product_list_with_text_search(async_client, mock_uow, patch_uow):
    unique = UniqueProductFactory.build(id=1, slug="truba", name="Труба одностінна")
    unique.images = [ProductImageFactory.build(id=1, product_id=1, file_path="uploads/truba/img.jpg", product=unique)]

    uow = mock_uow(
        {
            "unique_products": {
                "all": [unique],
                "count": 1,
            },
        },
    )

    async with patch_uow(uow):
        response = await async_client.get("/api/v1/products/unique?text=труба")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["pagination"]["total"] == 1
    assert payload["items"][0]["id"] == 1

    assert uow.unique_products.all.await_args.kwargs["filters"] == {
        "category_id": None,
        "text": "труба",
    }


@pytest.mark.asyncio
async def test_fetch_filters_success(async_client, mock_uow, patch_uow):
    uow = mock_uow(
        {
            "products": {
                "fetch_filters": ProductFiltersRepoResultFactory.build(),
                "get_min_max_price": (10.0, 200.0),
            },
        },
    )

    async with patch_uow(uow):
        response = await async_client.get("/api/v1/products/filters?slug=cat&text=q")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert "diameter" in payload
    assert "min_price" in payload
    assert "max_price" in payload


@pytest.mark.asyncio
async def test_get_products_recommendations_success(async_client, mock_uow, patch_uow):
    unique = UniqueProductFactory.build(id=1, slug="u-1", name="Unique 1")
    unique.images = [ProductImageFactory.build(id=1, product_id=1, file_path="uploads/u-1/img.jpg", product=unique)]
    variation = ProductVariationFactory.build(id=10, product_id=1, product=unique, price=100.0)

    uow = mock_uow(
        {
            "products": {
                "get_products_with_most_orders": [variation],
            },
            "website_settings": {"get_or_none": _default_ws},
        },
    )

    async with patch_uow(uow):
        response = await async_client.get("/api/v1/products/popular")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["pagination"]["total"] == 1
    assert payload["items"][0]["id"] == 10


@pytest.mark.asyncio
async def test_fetch_absolute_product_success(async_client, mock_uow, patch_uow):
    unique = UniqueProductFactory.build(id=1, slug="u-1", name="Unique 1", category_id=10)
    image = ProductImageFactory.build(id=1, product_id=1, file_path="uploads/u-1/img.jpg", product=unique)
    variation = ProductVariationFactory.build(id=10, product_id=1, price=100.0)
    category_chain = [
        CategoryFactory.build(id=10, name="Cat 1", slug="cat-1"),
        CategoryFactory.build(id=11, name="Cat 2", slug="cat-2"),
    ]

    uow = mock_uow(
        {
            "unique_products": {
                "exists": True,
                "get": unique,
            },
            "products_images": {
                "all": [image],
            },
            "products": {
                "all": [variation],
            },
            "categories": {
                "get_category_hierarchy": category_chain,
            },
            "website_settings": {"get_or_none": _default_ws},
        },
    )

    async with patch_uow(uow):
        response = await async_client.get("/api/v1/products/u-1")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["id"] == 1
    assert payload["slug"] == "u-1"
    assert payload["images"][0]["file_path"] == "uploads/u-1/img.jpg"
    assert payload["variations"][0]["id"] == 10
    assert payload["categories"] == [["Cat 1", "cat-1"], ["Cat 2", "cat-2"]]


@pytest.mark.asyncio
async def test_create_product_success(async_client, mock_uow, patch_uow, patch_superuser, monkeypatch):
    monkeypatch.setattr(AbstractFileStorageService, "verify_file", AsyncMock(return_value=True))
    monkeypatch.setattr(LocalFileStorage, "upload", AsyncMock(return_value=None))
    monkeypatch.setattr(LocalFileStorage, "cleanup_files", AsyncMock(return_value=None))
    monkeypatch.setattr(SupabaseFileStorage, "upload", AsyncMock(return_value=None))
    monkeypatch.setattr(SupabaseFileStorage, "cleanup_files", AsyncMock(return_value=None))

    unique = UniqueProductFactory.build(id=1, slug="prod-1", name="Product", category_id=1)
    created_image = ProductImageFactory.build(id=1, product_id=1, file_path="uploads/prod-1/img.jpg")
    created_variation = ProductVariationFactory.build(id=10, product_id=1, price=10.0)

    uow = mock_uow(
        {
            "unique_products": {
                "exists": False,
                "create": unique,
            },
            "categories": {
                "exists": True,
            },
            "products_images": {
                "bulk_create": [created_image],
            },
            "products": {
                "bulk_create": [created_variation],
            },
        },
    )
    uow.unique_products.exists.side_effect = lambda **kwargs: False if "slug" in kwargs else True

    variations = [{"price": 10.0, "discount_percentage": 0}]
    files = [("images", ("img.jpg", b"fake-bytes", "image/jpeg"))]
    data = {
        "name": "Product",
        "slug": "prod-1",
        "description": "Desc",
        "category_id": "1",
        "variations_json": json.dumps(variations),
    }

    async with patch_uow(uow), patch_superuser():
        response = await async_client.post("/api/v1/products", data=data, files=files)

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["id"] == 1
    assert payload["slug"] == "prod-1"
    assert payload["images"][0]["file_path"]
    assert payload["variations"][0]["id"] == 10


@pytest.mark.asyncio
async def test_create_product_validation_error_invalid_variations_schema(
    async_client,
    mock_uow,
    patch_uow,
    patch_superuser,
):
    variations = [{"discount_percentage": 0}]
    files = [("images", ("img.jpg", b"fake-bytes", "image/jpeg"))]
    data = {
        "name": "Product",
        "slug": "prod-1",
        "category_id": "1",
        "variations_json": json.dumps(variations),
    }

    uow = mock_uow({})
    async with patch_uow(uow), patch_superuser():
        response = await async_client.post("/api/v1/products", data=data, files=files)

    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_update_product_success(async_client, mock_uow, patch_uow, patch_superuser):
    updated = UniqueProductFactory.build(id=1, slug="prod-1", name="New name", category_id=1)
    new_variation = ProductVariationFactory.build(id=10, product_id=1, price=12.0)

    uow = mock_uow(
        {
            "unique_products": {
                "update": updated,
            },
            "products_images": {
                "bulk_delete": None,
            },
            "products": {
                "bulk_create": [new_variation],
            },
        },
    )
    uow.unique_products.exists = AsyncMock(return_value=True)

    data = {
        "name": "New name",
        "slug": "prod-1",
        "variations_json": json.dumps([{"action": "create", "price": 12.0}]),
    }

    async with patch_uow(uow), patch_superuser():
        response = await async_client.patch("/api/v1/products/1", data=data)

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["id"] == 1
    assert payload["slug"] == "prod-1"
    assert payload["variations"][0]["id"] == 10


@pytest.mark.asyncio
async def test_delete_unique_success(async_client, mock_uow, patch_uow, patch_superuser):
    unique = UniqueProductFactory.build(id=1, slug="u-1", name="Unique 1")

    uow = mock_uow(
        {
            "unique_products": {
                "exists": True,
                "get": unique,
                "delete": None,
            },
        },
    )

    async with patch_uow(uow), patch_superuser():
        response = await async_client.delete("/api/v1/products/unique/1")

    assert response.status_code == 200
    assert response.content in (b"", b"null")
