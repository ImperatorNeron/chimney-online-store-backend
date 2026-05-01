import pytest
from tests.factories.products import ProductImageFactory, ProductVariationFactory, UniqueProductFactory

from app.models.website_settings import WebSiteSettings


def _ws(discount: float, markup: float, **kwargs):
    return WebSiteSettings(id=1, manufacturer_discount=discount, seller_markup=markup, **kwargs)


def _make_variation(price: float, discount_percentage: int = 0):
    unique = UniqueProductFactory.build(id=1, slug="u-1", name="Unique 1")
    unique.images = [ProductImageFactory.build(id=1, product_id=1, file_path="img.jpg", product=unique)]
    return ProductVariationFactory.build(
        id=10, product_id=1,
        product=unique,
        price=price,
        discount_percentage=discount_percentage,
    )


@pytest.mark.asyncio
async def test_catalog_product_price_with_website_settings(async_client, mock_uow, patch_uow):
    """Catalog endpoint applies manufacturer discount then seller markup."""
    variation = _make_variation(price=1000.0, discount_percentage=0)

    uow = mock_uow({
        "products": {"list_product_previews": [variation], "count": 1},
        "website_settings": {"get_or_none": _ws(10, 50)},
    })

    async with patch_uow(uow):
        response = await async_client.get("/api/v1/products?offset=0")

    assert response.status_code == 200
    item = response.json()["data"]["items"][0]
    # 1000 * (1 - 10/100) * (1 + 50/100) = 1000 * 0.9 * 1.5 = 1350
    assert item["price"] == 1350
    assert item["discount_price"] == 1350


@pytest.mark.asyncio
async def test_catalog_product_price_with_settings_and_variation_discount(async_client, mock_uow, patch_uow):
    """Website settings + per-variation discount_percentage stack correctly."""
    variation = _make_variation(price=1000.0, discount_percentage=20)

    uow = mock_uow({
        "products": {"list_product_previews": [variation], "count": 1},
        "website_settings": {"get_or_none": _ws(10, 50)},
    })

    async with patch_uow(uow):
        response = await async_client.get("/api/v1/products?offset=1")

    assert response.status_code == 200
    item = response.json()["data"]["items"][0]
    # adjusted = 1000 * 0.9 * 1.5 = 1350, then 20% discount: 1350 - 270 = 1080
    assert item["price"] == 1350
    assert item["discount_price"] == 1080


@pytest.mark.asyncio
async def test_catalog_product_price_with_zero_settings(async_client, mock_uow, patch_uow):
    """With 0% settings, prices remain unchanged."""
    variation = _make_variation(price=100.0, discount_percentage=10)

    uow = mock_uow({
        "products": {"list_product_previews": [variation], "count": 1},
        "website_settings": {"get_or_none": _ws(0, 0)},
    })

    async with patch_uow(uow):
        response = await async_client.get("/api/v1/products?offset=2")

    assert response.status_code == 200
    item = response.json()["data"]["items"][0]
    assert item["price"] == 100
    assert item["discount_price"] == 90


@pytest.mark.asyncio
async def test_admin_variations_show_original_price(async_client, mock_uow, patch_uow, patch_superuser):
    """Admin /{slug}/variations endpoint shows original prices without
    settings."""
    unique = UniqueProductFactory.build(id=1, slug="u-1", name="Unique 1", category_id=10)
    image = ProductImageFactory.build(id=1, product_id=1, file_path="img.jpg", product=unique)
    variation = ProductVariationFactory.build(id=10, product_id=1, price=1000.0, discount_percentage=0)

    uow = mock_uow({
        "unique_products": {"exists": True, "get": unique},
        "products_images": {"all": [image]},
        "products": {"all": [variation], "count": 1},
        "categories": {"get_category_hierarchy": []},
        "website_settings": {"get_or_none": _ws(10, 50)},
    })

    async with patch_uow(uow), patch_superuser():
        response = await async_client.get("/api/v1/products/u-1/variations")

    assert response.status_code == 200
    v = response.json()["data"]["variations"][0]
    # No settings applied — original price
    assert v["price"] == 1000
    assert v["discount_price"] == 1000


@pytest.mark.asyncio
async def test_get_website_settings(async_client, mock_uow, patch_uow, patch_superuser):
    uow = mock_uow({
        "website_settings": {"get_or_none": _ws(15, 25)},
    })

    async with patch_uow(uow), patch_superuser():
        response = await async_client.get("/api/v1/website-settings")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["manufacturer_discount"] == 15
    assert data["seller_markup"] == 25


@pytest.mark.asyncio
async def test_update_website_settings(async_client, mock_uow, patch_uow, patch_superuser):
    updated = _ws(20, 30)

    uow = mock_uow({
        "website_settings": {
            "get_or_none": _ws(0, 0),
            "update": updated,
        },
    })

    async with patch_uow(uow), patch_superuser():
        response = await async_client.patch(
            "/api/v1/website-settings",
            json={"manufacturer_discount": 20, "seller_markup": 30},
        )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["manufacturer_discount"] == 20
    assert data["seller_markup"] == 30


@pytest.mark.asyncio
async def test_update_website_settings_unauthorized(async_client):
    response = await async_client.patch(
        "/api/v1/website-settings",
        json={"manufacturer_discount": 10},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_public_website_settings_no_auth_required(async_client, mock_uow, patch_uow):
    ws = _ws(
        10, 20, phone="+380991234567", email="test@example.com",
        address="м. Луцьк", work_schedule="Пн-Пт: 9:00-18:00",
        telegram_url="https://t.me/test", facebook_url="https://facebook.com/test",
    )

    uow = mock_uow({"website_settings": {"get_or_none": ws}})

    async with patch_uow(uow):
        response = await async_client.get("/api/v1/website-settings/public")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["phone"] == "+380991234567"
    assert data["email"] == "test@example.com"
    assert data["address"] == "м. Луцьк"
    assert data["work_schedule"] == "Пн-Пт: 9:00-18:00"
    assert data["telegram_url"] == "https://t.me/test"
    assert data["facebook_url"] == "https://facebook.com/test"
    assert data["manufacturer_discount"] == 10
    assert data["seller_markup"] == 20


@pytest.mark.asyncio
async def test_get_public_website_settings_with_null_fields(async_client, mock_uow, patch_uow):
    ws = _ws(0, 0)

    uow = mock_uow({"website_settings": {"get_or_none": ws}})

    async with patch_uow(uow):
        response = await async_client.get("/api/v1/website-settings/public")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["phone"] is None
    assert data["email"] is None
    assert data["address"] is None
    assert data["work_schedule"] is None
    assert data["telegram_url"] is None
    assert data["facebook_url"] is None


@pytest.mark.asyncio
async def test_update_website_settings_with_contact_fields(async_client, mock_uow, patch_uow, patch_superuser):
    updated = _ws(
        10, 20, phone="+380501234567", email="info@shop.com",
        address="м. Київ", work_schedule="Пн-Сб: 9:00-19:00",
        telegram_url="https://t.me/shop", facebook_url="https://facebook.com/shop",
    )

    uow = mock_uow({
        "website_settings": {
            "get_or_none": _ws(0, 0),
            "update": updated,
        },
    })

    async with patch_uow(uow), patch_superuser():
        response = await async_client.patch(
            "/api/v1/website-settings",
            json={
                "manufacturer_discount": 10,
                "seller_markup": 20,
                "phone": "+380501234567",
                "email": "info@shop.com",
                "address": "м. Київ",
                "work_schedule": "Пн-Сб: 9:00-19:00",
                "telegram_url": "https://t.me/shop",
                "facebook_url": "https://facebook.com/shop",
            },
        )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["phone"] == "+380501234567"
    assert data["email"] == "info@shop.com"
    assert data["address"] == "м. Київ"
    assert data["work_schedule"] == "Пн-Сб: 9:00-19:00"
    assert data["telegram_url"] == "https://t.me/shop"
    assert data["facebook_url"] == "https://facebook.com/shop"


@pytest.mark.asyncio
async def test_get_website_settings_unauthorized(async_client):
    response = await async_client.get("/api/v1/website-settings")
    assert response.status_code == 401
