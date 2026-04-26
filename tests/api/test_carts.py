from unittest.mock import AsyncMock

import pytest
from tests.factories.products import ProductImageFactory, ProductVariationFactory, UniqueProductFactory

from app.core.exceptions.common import ItemNotFoundException
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.website_settings import WebSiteSettings
from app.services.tokens import JWTTokenService


_default_ws = WebSiteSettings(id=1, manufacturer_discount=0, seller_markup=0)


def _cart_create_side_effect(cart_id: int = 1):
    async def _create(*, item_in: Cart):
        item_in.id = cart_id
        item_in.items = []
        return item_in

    return _create


def _cart_item_create_side_effect(item_id: int = 1):
    async def _create(*, item_in: CartItem):
        item_in.id = item_id
        return item_in

    return _create


@pytest.mark.asyncio
async def test_get_cart_anonymous_creates_new_cart_and_sets_cookie(
    async_client, mock_uow, patch_uow,
):
    uow = mock_uow({"cart": {"create": None}})
    uow.cart.create = AsyncMock(side_effect=_cart_create_side_effect(cart_id=1))

    async with patch_uow(uow):
        response = await async_client.get("/api/v1/cart")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["id"] == 1
    assert payload["items"] == []
    assert payload["total_price"] == 0
    assert payload["total_quantity"] == 0
    assert response.cookies.get("cart_session_id")


@pytest.mark.asyncio
async def test_get_cart_anonymous_with_existing_cookie_fetches_cart_and_returns_totals(
    async_client,
    mock_uow,
    patch_uow,
):
    unique = UniqueProductFactory.build(id=1, slug="u-1", name="Unique 1")
    unique.images = [
        ProductImageFactory.build(
            id=1,
            product_id=1,
            file_path="uploads/u-1/img.jpg",
            product=unique,
        ),
    ]
    variation_1 = ProductVariationFactory.build(
        id=10,
        product_id=1,
        product=unique,
        price=100.0,
        discount_percentage=0,
    )
    variation_2 = ProductVariationFactory.build(
        id=11,
        product_id=1,
        product=unique,
        price=50.0,
        discount_percentage=10,
    )

    cart_item_1 = CartItem(cart_id=1, product_id=10, quantity=2, product=variation_1)
    cart_item_1.id = 1
    cart_item_2 = CartItem(cart_id=1, product_id=11, quantity=3, product=variation_2)
    cart_item_2.id = 2

    cart = Cart(session_id="s" * 32)
    cart.id = 1
    cart.items = [cart_item_1, cart_item_2]

    uow = mock_uow({"cart": {"get": cart}, "website_settings": {"get_or_none": _default_ws}})

    async with patch_uow(uow):
        response = await async_client.get(
            "/api/v1/cart",
            cookies={"cart_session_id": "s" * 32},
        )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["id"] == 1
    assert payload["total_quantity"] == 5
    assert (
        payload["total_price"] == 335
    )  # variation_1: 2 * 100 = 200 variation_2: 50 - 10% = 45, 3 * 45 = 135
    assert len(payload["items"]) == 2
    assert {item["product"]["id"] for item in payload["items"]} == {10, 11}


@pytest.mark.asyncio
async def test_get_cart_anonymous_cookie_cart_not_found_creates_new_cart(
    async_client, mock_uow, patch_uow,
):
    uow = mock_uow({"cart": {"get": None, "create": None}, "website_settings": {"get_or_none": _default_ws}})
    uow.cart.get = AsyncMock(side_effect=ItemNotFoundException())
    uow.cart.create = AsyncMock(side_effect=_cart_create_side_effect(cart_id=1))

    async with patch_uow(uow):
        response = await async_client.get(
            "/api/v1/cart",
            cookies={"cart_session_id": "s" * 32},
        )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["items"] == []
    assert payload["total_quantity"] == 0
    assert payload["total_price"] == 0
    assert response.cookies.get("cart_session_id")


@pytest.mark.asyncio
async def test_get_cart_authenticated_merges_session_cart_and_deletes_cookie(
    async_client,
    mock_uow,
    patch_uow,
):
    token_service = JWTTokenService()
    access_token = await token_service.create_access_token(pk=1, username="user")

    unique = UniqueProductFactory.build(id=1, slug="u-1", name="Unique 1")
    unique.images = [
        ProductImageFactory.build(
            id=1,
            product_id=1,
            file_path="uploads/u-1/img.jpg",
            product=unique,
        ),
    ]
    v1 = ProductVariationFactory.build(
        id=10, product_id=1, product=unique, price=100.0, discount_percentage=0,
    )
    v3 = ProductVariationFactory.build(
        id=12, product_id=1, product=unique, price=20.0, discount_percentage=0,
    )

    # user cart: [v1 x1]
    user_cart_item = CartItem(cart_id=1, product_id=10, quantity=1, product=v1)
    user_cart_item.id = 1
    user_cart = Cart(user_id=1)
    user_cart.id = 1
    user_cart.items = [user_cart_item]

    # session cart: [v1 x2] + [v3 x1]
    session_cart_item_1 = CartItem(cart_id=2, product_id=10, quantity=2, product=v1)
    session_cart_item_1.id = 2
    session_cart_item_2 = CartItem(cart_id=2, product_id=12, quantity=1, product=v3)
    session_cart_item_2.id = 3
    session_cart = Cart(session_id="s" * 32)
    session_cart.id = 2
    session_cart.items = [session_cart_item_1, session_cart_item_2]

    uow = mock_uow(
        {
            "cart": {"get": None, "delete": None, "exists": True},
            "products": {"exists": True},
            "cart_item": {"exists": False, "create": None, "increase_quantity": None, "count": 1},
            "website_settings": {"get_or_none": _default_ws},
        },
    )

    async def _cart_get(**kwargs):
        if kwargs.get("user_id") == 1:
            return user_cart
        if kwargs.get("session_id") == "s" * 32:
            return session_cart
        raise ItemNotFoundException()

    uow.cart.get = AsyncMock(side_effect=_cart_get)
    uow.cart.delete = AsyncMock(return_value=None)
    uow.cart_item.create = AsyncMock(
        side_effect=_cart_item_create_side_effect(item_id=50),
    )

    async def _cart_item_exists(**kwargs):
        # existing cart item check for create() inside merge for v3 (new) -> False
        if "cart_id" in kwargs and "product_id" in kwargs:
            return False
        # increase quantity path for v1 existing in user_cart -> True
        if "id" in kwargs and "cart_id" in kwargs:
            return True
        return False

    uow.cart_item.exists = AsyncMock(side_effect=_cart_item_exists)

    updated_v1_item = CartItem(cart_id=1, product_id=10, quantity=3)
    updated_v1_item.id = 1
    uow.cart_item.increase_quantity = AsyncMock(return_value=updated_v1_item)

    async with patch_uow(uow):
        response = await async_client.get(
            "/api/v1/cart",
            headers={"Authorization": f"Bearer {access_token}"},
            cookies={"cart_session_id": "s" * 32},
        )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["id"] == 1
    assert payload["total_quantity"] == 4
    assert payload["total_price"] == 320
    assert len(payload["items"]) == 2
    assert any("Max-Age=0" in v for v in response.headers.get_list("set-cookie"))


@pytest.mark.asyncio
async def test_add_to_cart_success_creates_item_and_sets_cookie(
    async_client,
    mock_uow,
    patch_uow,
):
    uow = mock_uow(
        {
            "cart": {"create": None, "exists": True},
            "products": {"exists": True},
            "cart_item": {"exists": False, "create": None, "count": 0},
        },
    )
    uow.cart.create = AsyncMock(side_effect=_cart_create_side_effect(cart_id=1))
    uow.cart_item.create = AsyncMock(
        side_effect=_cart_item_create_side_effect(item_id=5),
    )

    async with patch_uow(uow):
        response = await async_client.post(
            "/api/v1/cart",
            json={"quantity": 2, "product_id": 10},
        )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["id"] == 5
    assert payload["cart_id"] == 1
    assert payload["product_id"] == 10
    assert payload["quantity"] == 2
    assert response.cookies.get("cart_session_id")


@pytest.mark.asyncio
async def test_add_to_cart_when_item_exists_increases_quantity(
    async_client,
    mock_uow,
    patch_uow,
):
    existing = CartItem(cart_id=1, product_id=10, quantity=1)
    existing.id = 5
    increased = CartItem(cart_id=1, product_id=10, quantity=3)
    increased.id = 5

    uow = mock_uow(
        {
            "cart": {"create": None, "exists": True},
            "products": {"exists": True},
            "cart_item": {
                "exists": True,
                "get": existing,
                "increase_quantity": increased,
            },
        },
    )
    uow.cart.create = AsyncMock(side_effect=_cart_create_side_effect(cart_id=1))

    async def _exists(**kwargs):
        if "cart_id" in kwargs and "product_id" in kwargs:
            return True
        if "id" in kwargs and "cart_id" in kwargs:
            return True
        return False

    uow.cart_item.exists = AsyncMock(side_effect=_exists)

    async with patch_uow(uow):
        response = await async_client.post(
            "/api/v1/cart",
            json={"quantity": 2, "product_id": 10},
        )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["id"] == 5
    assert payload["quantity"] == 3


@pytest.mark.asyncio
async def test_add_to_cart_fk_error_when_product_missing(
    async_client, mock_uow, patch_uow,
):
    uow = mock_uow(
        {
            "cart": {"create": None, "exists": True},
            "products": {"exists": False},
            "cart_item": {"exists": False},
        },
    )
    uow.cart.create = AsyncMock(side_effect=_cart_create_side_effect(cart_id=1))

    async with patch_uow(uow):
        response = await async_client.post(
            "/api/v1/cart",
            json={"quantity": 1, "product_id": 999},
        )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_cart_item_quantity_increment_success(
    async_client,
    mock_uow,
    patch_uow,
):
    updated = CartItem(cart_id=1, product_id=10, quantity=3)
    updated.id = 5

    uow = mock_uow(
        {
            "cart": {"create": None},
            "cart_item": {"exists": True, "increase_quantity": updated},
        },
    )
    uow.cart.create = AsyncMock(side_effect=_cart_create_side_effect(cart_id=1))

    async with patch_uow(uow):
        response = await async_client.patch(
            "/api/v1/cart/change-item-quantity/5",
            json={"action": "increment", "quantity": 2},
        )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["id"] == 5
    assert payload["quantity"] == 3


@pytest.mark.asyncio
async def test_update_cart_item_quantity_not_found(async_client, mock_uow, patch_uow):
    uow = mock_uow({"cart": {"create": None}, "cart_item": {"exists": False}})
    uow.cart.create = AsyncMock(side_effect=_cart_create_side_effect(cart_id=1))

    async with patch_uow(uow):
        response = await async_client.patch(
            "/api/v1/cart/change-item-quantity/5",
            json={"action": "increment", "quantity": 1},
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_remove_item_from_cart_success(async_client, mock_uow, patch_uow):
    uow = mock_uow({"cart": {"create": None}, "cart_item": {"delete": None}})
    uow.cart.create = AsyncMock(side_effect=_cart_create_side_effect(cart_id=1))

    async with patch_uow(uow):
        response = await async_client.delete("/api/v1/cart/5")

    assert response.status_code == 200
    assert response.content in (b"", b"null")


@pytest.mark.asyncio
async def test_merge_carts_caps_quantity_at_100(
    async_client,
    mock_uow,
    patch_uow,
):
    """When merging, if combined quantity exceeds 100, it should be capped at
    100."""
    token_service = JWTTokenService()
    access_token = await token_service.create_access_token(pk=1, username="user")

    unique = UniqueProductFactory.build(id=1, slug="u-1", name="Unique 1")
    unique.images = [
        ProductImageFactory.build(id=1, product_id=1, file_path="uploads/u-1/img.jpg", product=unique),
    ]
    v1 = ProductVariationFactory.build(
        id=10, product_id=1, product=unique, price=100.0, discount_percentage=0,
    )

    # user cart: v1 x 90
    user_cart_item = CartItem(cart_id=1, product_id=10, quantity=90, product=v1)
    user_cart_item.id = 1
    user_cart = Cart(user_id=1)
    user_cart.id = 1
    user_cart.items = [user_cart_item]

    # session cart: v1 x 50 (should only add 10 to reach cap of 100)
    session_cart_item = CartItem(cart_id=2, product_id=10, quantity=50, product=v1)
    session_cart_item.id = 2
    session_cart = Cart(session_id="s" * 32)
    session_cart.id = 2
    session_cart.items = [session_cart_item]

    uow = mock_uow(
        {
            "cart": {"get": None, "delete": None, "exists": True},
            "cart_item": {"exists": True, "increase_quantity": None},
            "website_settings": {"get_or_none": _default_ws},
        },
    )

    async def _cart_get(**kwargs):
        if kwargs.get("user_id") == 1:
            return user_cart
        if kwargs.get("session_id") == "s" * 32:
            return session_cart
        raise ItemNotFoundException()

    uow.cart.get = AsyncMock(side_effect=_cart_get)
    uow.cart.delete = AsyncMock(return_value=None)

    updated_item = CartItem(cart_id=1, product_id=10, quantity=100)
    updated_item.id = 1
    uow.cart_item.increase_quantity = AsyncMock(return_value=updated_item)

    async with patch_uow(uow):
        response = await async_client.get(
            "/api/v1/cart",
            headers={"Authorization": f"Bearer {access_token}"},
            cookies={"cart_session_id": "s" * 32},
        )

    assert response.status_code == 200
    payload = response.json()["data"]
    # Should have capped: 90 + min(50, 100-90) = 90 + 10 = 100
    assert payload["total_quantity"] == 100
    assert payload["total_price"] == 10000  # 100 * 100.0
    # increase_quantity called with quantity=10 (not 50)
    uow.cart_item.increase_quantity.assert_awaited_once_with(
        quantity=10, cart_item_id=1,
    )
