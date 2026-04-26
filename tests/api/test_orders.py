from unittest.mock import AsyncMock

import pytest
from tests.factories.orders import OrderFactory, OrderItemFactory
from tests.factories.products import ProductImageFactory, ProductVariationFactory, UniqueProductFactory
from tests.factories.users import ReadUserFactory, UserFactory

from app.core.exceptions.common import ItemNotFoundException
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.orders import OrderItem
from app.models.website_settings import WebSiteSettings
from app.services.tokens import JWTTokenService


_default_ws = WebSiteSettings(id=1, manufacturer_discount=0, seller_markup=0)


def _build_variation(*, variation_id: int, unique_id: int, slug: str, price: float, discount_percentage: int):
    unique = UniqueProductFactory.build(id=unique_id, slug=slug, name=f"Unique {unique_id}")
    unique.images = [
        ProductImageFactory.build(
            id=unique_id,
            product_id=unique_id,
            file_path=f"uploads/{slug}/img.jpg",
            product=unique,
        ),
    ]
    return ProductVariationFactory.build(
        id=variation_id,
        product_id=unique_id,
        product=unique,
        price=price,
        discount_percentage=discount_percentage,
    )


def _build_cart_with_items(*, cart_id: int, session_id: str, items: list[tuple]):
    """
    items: list[(CartItem.id, ProductVariation, quantity)]
    """
    cart = Cart(session_id=session_id)
    cart.id = cart_id
    cart.items = []
    for item_id, variation, quantity in items:
        cart_item = CartItem(cart_id=cart_id, product_id=variation.id, quantity=quantity, product=variation)
        cart_item.id = item_id
        cart.items.append(cart_item)
    return cart


def _order_item_bulk_create_side_effect(expected: list[dict], order_item_ids: list[int]):
    async def _bulk_create(*, data_list: list[OrderItem]):
        assert len(data_list) == len(expected)
        for created, exp, new_id in zip(data_list, expected, order_item_ids, strict=False):
            assert created.order_id == exp["order_id"]
            assert created.product_id == exp["product_id"]
            assert created.quantity == exp["quantity"]
            assert float(created.price_at_order) == exp["price_at_order"]
            created.id = new_id
        return data_list

    return _bulk_create


@pytest.mark.asyncio
async def test_get_orders_list_success_as_superuser(async_client, mock_uow, patch_uow, patch_superuser):
    v1 = _build_variation(
        variation_id=10,
        unique_id=1,
        slug="u-1",
        price=100.0,
        discount_percentage=0,
    )
    v2 = _build_variation(
        variation_id=11,
        unique_id=2,
        slug="u-2",
        price=50.0,
        discount_percentage=10,
    )

    o1 = OrderFactory.build(id=1, status="processing", user_id=1)
    i11 = OrderItemFactory.build(id=1, order_id=1, product_id=10, quantity=2, price_at_order=200.0, product=v1)
    i12 = OrderItemFactory.build(id=2, order_id=1, product_id=11, quantity=1, price_at_order=45.0, product=v2)
    o1.items = [i11, i12]

    o2 = OrderFactory.build(id=2, status="pending", user_id=2)
    i21 = OrderItemFactory.build(id=3, order_id=2, product_id=10, quantity=1, price_at_order=100.0, product=v1)
    o2.items = [i21]

    uow = mock_uow(
        {
            "order": {
                "all": [o1, o2],
                "count": 2,
            },
        },
    )

    async with patch_uow(uow), patch_superuser():
        response = await async_client.get("/api/v1/orders?offset=0&limit=20")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["pagination"]["total"] == 2
    assert len(payload["items"]) == 2
    assert payload["items"][0]["id"] == 1
    assert payload["items"][0]["total_quantity"] == 3
    assert payload["items"][0]["total_price"] == 245
    assert payload["items"][1]["id"] == 2
    assert payload["items"][1]["total_quantity"] == 1
    assert payload["items"][1]["total_price"] == 100
    uow.order.all.assert_awaited_once()
    assert uow.order.all.await_args.kwargs["order_by"] == ["-created_at"]


@pytest.mark.asyncio
async def test_get_orders_list_success_with_sorting(
    async_client,
    mock_uow,
    patch_uow,
    patch_superuser,
):
    o1 = OrderFactory.build(id=1, status="processing", user_id=1)
    uow = mock_uow({"order": {"all": [o1], "count": 1}})

    async with patch_uow(uow), patch_superuser():
        response = await async_client.get("/api/v1/orders?field=id&ordering=asc")

    assert response.status_code == 200
    uow.order.all.assert_awaited_once()
    assert uow.order.all.await_args.kwargs["order_by"] == ["id"]


@pytest.mark.asyncio
async def test_get_orders_list_success_with_text_search(
    async_client,
    mock_uow,
    patch_uow,
    patch_superuser,
):
    o1 = OrderFactory.build(id=1, status="processing", user_id=1, first_name="Ivan", last_name="Ivanov")
    uow = mock_uow({"order": {"all": [o1], "count": 1}})

    async with patch_uow(uow), patch_superuser():
        response = await async_client.get("/api/v1/orders?text=Ivan")

    assert response.status_code == 200
    uow.order.all.assert_awaited_once()
    assert uow.order.all.await_args.kwargs["filters"] == {
        "text": "Ivan",
        "status": None,
        "shipping_method": None,
        "payment_method": None,
        "date_from": None,
        "date_to": None,
    }


@pytest.mark.asyncio
async def test_get_orders_list_unauthorized_without_user(async_client):
    response = await async_client.get("/api/v1/orders")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_orders_history_success(async_client, mock_uow, patch_uow, patch_auth_user):
    user = ReadUserFactory.build(id=1)

    v1 = _build_variation(variation_id=10, unique_id=1, slug="u-1", price=100.0, discount_percentage=0)
    v2 = _build_variation(variation_id=11, unique_id=2, slug="u-2", price=50.0, discount_percentage=0)

    delivered = OrderFactory.build(id=1, status="delivered", user_id=1)
    d1 = OrderItemFactory.build(id=1, order_id=1, product_id=10, quantity=1, price_at_order=100.0, product=v1)
    d2 = OrderItemFactory.build(id=2, order_id=1, product_id=11, quantity=2, price_at_order=100.0, product=v2)
    delivered.items = [d1, d2]

    cancelled = OrderFactory.build(id=2, status="cancelled", user_id=1)
    c1 = OrderItemFactory.build(id=3, order_id=2, product_id=11, quantity=1, price_at_order=50.0, product=v2)
    cancelled.items = [c1]

    uow = mock_uow({"order": {"finished_orders_by_user_id": [delivered, cancelled], "count": 2}})

    async with patch_uow(uow), patch_auth_user(user):
        response = await async_client.get("/api/v1/orders/history")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["pagination"]["total"] == 2
    assert len(payload["items"]) == 2
    assert payload["items"][0]["id"] == 1
    assert payload["items"][0]["total_quantity"] == 3
    assert payload["items"][0]["total_price"] == 200


@pytest.mark.asyncio
async def test_get_orders_history_unauthorized_without_user(async_client):
    response = await async_client.get("/api/v1/orders/history")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_active_orders_success(async_client, mock_uow, patch_uow, patch_auth_user):
    user = ReadUserFactory.build(id=1)

    v1 = _build_variation(variation_id=10, unique_id=1, slug="u-1", price=100.0, discount_percentage=0)
    v2 = _build_variation(variation_id=11, unique_id=2, slug="u-2", price=50.0, discount_percentage=0)

    processing = OrderFactory.build(id=1, status="processing", user_id=1)
    p1 = OrderItemFactory.build(id=1, order_id=1, product_id=10, quantity=1, price_at_order=100.0, product=v1)
    processing.items = [p1]

    shipped = OrderFactory.build(id=2, status="shipped", user_id=1)
    s1 = OrderItemFactory.build(id=2, order_id=2, product_id=11, quantity=2, price_at_order=100.0, product=v2)
    shipped.items = [s1]

    uow = mock_uow({"order": {"current_orders_by_user_id": [processing, shipped], "count": 2}})

    async with patch_uow(uow), patch_auth_user(user):
        response = await async_client.get("/api/v1/orders/active")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["pagination"]["total"] == 2
    assert len(payload["items"]) == 2
    assert {o["status"] for o in payload["items"]} == {"processing", "shipped"}


@pytest.mark.asyncio
async def test_update_order_info_success_waybill_empty_becomes_none(
    async_client,
    mock_uow,
    patch_uow,
    patch_superuser,
):
    updated = OrderFactory.build(
        id=1,
        status="processing",
        waybill_number=None,
        price_discount=10.0,
        is_paid=True,
        shipping_method="nova_poshta",
        payment_method="cash",
        first_name="Ivan",
        last_name="Ivanov",
    )

    async def _update(*, id: int, item_in): # noqa
        assert id == 1
        assert getattr(item_in, "waybill_number", None) is None
        assert getattr(item_in, "is_paid", None) is True
        assert getattr(item_in, "shipping_method", None) == "nova_poshta"
        assert getattr(item_in, "payment_method", None) == "cash"
        assert getattr(item_in, "first_name", None) == "Ivan"
        assert getattr(item_in, "last_name", None) == "Ivanov"
        return updated

    uow = mock_uow({"order": {"update": updated}})
    uow.order.update = AsyncMock(side_effect=_update)

    async with patch_uow(uow), patch_superuser():
        response = await async_client.patch(
            "/api/v1/orders/1",
            json={
                "status": "processing",
                "waybill_number": "",
                "price_discount": 10.0,
                "is_paid": True,
                "shipping_method": "nova_poshta",
                "payment_method": "cash",
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "patronymic": "Ivanovych",
                "email": "test@example.com",
                "phone_number": "0961234567",
                "address": "Kyiv, st. 1",
            },
        )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["id"] == 1
    assert payload["status"] == "processing"
    assert payload["waybill_number"] is None
    assert payload["price_discount"] == 10.0


@pytest.mark.asyncio
async def test_update_order_info_validation_error_invalid_status(async_client, patch_superuser):
    async with patch_superuser():
        response = await async_client.patch(
            "/api/v1/orders/1",
            json={"status": "bad", "waybill_number": None, "price_discount": 0},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_order_success_anonymous_from_session_cart(
    async_client,
    mock_uow,
    patch_uow,
):
    v1 = _build_variation(variation_id=10, unique_id=1, slug="u-1", price=100.0, discount_percentage=0)
    v2 = _build_variation(variation_id=11, unique_id=2, slug="u-2", price=50.0, discount_percentage=10)

    cart = _build_cart_with_items(
        cart_id=1,
        session_id="s" * 32,
        items=[
            (1, v1, 2),
            (2, v2, 1),
        ],
    )

    created_order = OrderFactory.build(
        id=100,
        user_id=None,
        status="pending",
        shipping_method="nova_poshta",
        payment_method="cash",
    )

    async def _order_create(*, item_in):
        assert getattr(item_in, "user_id", None) is None
        return created_order

    expected_items = [
        {"order_id": 100, "product_id": 10, "quantity": 2, "price_at_order": 200.0},
        {"order_id": 100, "product_id": 11, "quantity": 1, "price_at_order": 45.0},
    ]

    uow = mock_uow(
        {
            "cart": {"get": cart, "delete": None},
            "order": {"create": created_order},
            "order_item": {"bulk_create": []},
            "website_settings": {"get_or_none": _default_ws},
        },
    )
    uow.order.create = AsyncMock(side_effect=_order_create)
    uow.order_item.bulk_create = AsyncMock(
        side_effect=_order_item_bulk_create_side_effect(expected_items, [1, 2]),
    )

    async with patch_uow(uow):
        response = await async_client.post(
            "/api/v1/orders",
            cookies={"cart_session_id": "s" * 32},
            json={
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "patronymic": "Ivanovych",
                "phone_number": "0961234567",
                "email": "test@example.com",
                "address": "Kyiv, st. 1",
                "shipping_method": "nova_poshta",
                "payment_method": "cash",
            },
        )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["id"] == 100
    assert payload["status"] == "pending"
    uow.cart.delete.assert_awaited()


@pytest.mark.asyncio
async def test_create_order_empty_cart_returns_409_and_sets_cookie(
    async_client,
    mock_uow,
    patch_uow,
):
    cart = Cart(session_id="s" * 32)
    cart.id = 1
    cart.items = []

    async def _cart_create(*, item_in):
        item_in.id = 1
        item_in.items = []
        return item_in

    uow = mock_uow({"cart": {"create": None}})
    uow.cart.create = AsyncMock(side_effect=_cart_create)

    async with patch_uow(uow):
        response = await async_client.post(
            "/api/v1/orders",
            json={
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "patronymic": "Ivanovych",
                "phone_number": "0961234567",
                "email": "test@example.com",
                "address": "Kyiv, st. 1",
                "shipping_method": "nova_poshta",
                "payment_method": "cash",
            },
        )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_order_authenticated_merges_session_cart_and_creates_for_user(
    async_client,
    mock_uow,
    patch_uow,
):
    token_service = JWTTokenService()
    access_token = await token_service.create_access_token(pk=1, username="user")

    v1 = _build_variation(variation_id=10, unique_id=1, slug="u-1", price=100.0, discount_percentage=0)
    v2 = _build_variation(variation_id=11, unique_id=2, slug="u-2", price=50.0, discount_percentage=0)

    # user cart: v1 x1
    user_cart = _build_cart_with_items(cart_id=1, session_id="", items=[(1, v1, 1)])
    user_cart.user_id = 1

    # session cart: v1 x2 + v2 x1
    session_cart = _build_cart_with_items(cart_id=2, session_id="s" * 32, items=[(2, v1, 2), (3, v2, 1)])

    created_order = OrderFactory.build(id=100, user_id=1)

    async def _cart_get(**kwargs):
        if kwargs.get("user_id") == 1:
            return user_cart
        if kwargs.get("session_id") == "s" * 32:
            return session_cart
        raise ItemNotFoundException()

    async def _order_create(*, item_in):
        assert getattr(item_in, "user_id", None) == 1
        return created_order

    expected_items = [
        {"order_id": 100, "product_id": 10, "quantity": 3, "price_at_order": 300.0},
        {"order_id": 100, "product_id": 11, "quantity": 1, "price_at_order": 50.0},
    ]

    increased_item = CartItem(cart_id=1, product_id=10, quantity=3)
    increased_item.id = 1

    user = UserFactory.build(id=1, username="user")

    uow = mock_uow(
        {
            "users": {"get": user},
            "cart": {"get": None, "create": None, "delete": None, "exists": True},
            "products": {"exists": True},
            "cart_item": {
                "exists": False,
                "get": None,
                "increase_quantity": increased_item,
                "create": None,
                "count": 1,
            },
            "order": {"create": created_order},
            "order_item": {"bulk_create": []},
            "website_settings": {"get_or_none": _default_ws},
        },
    )
    uow.cart.get = AsyncMock(side_effect=_cart_get)
    uow.cart.delete = AsyncMock(return_value=None)
    uow.order.create = AsyncMock(side_effect=_order_create)
    uow.order_item.bulk_create = AsyncMock(
        side_effect=_order_item_bulk_create_side_effect(expected_items, [1, 2]),
    )

    async def _cart_item_exists(**kwargs):
        # merge flow: existing in user_cart for v1 -> True on (id, cart_id)
        if "id" in kwargs and "cart_id" in kwargs:
            return True
        # create() existence check for (cart_id, product_id) for v2 -> False
        if "cart_id" in kwargs and "product_id" in kwargs:
            return False
        return False

    uow.cart_item.exists = AsyncMock(side_effect=_cart_item_exists)

    async def _cart_item_create(*, item_in):
        item_in.id = 50
        return item_in

    uow.cart_item.create = AsyncMock(side_effect=_cart_item_create)
    uow.cart_item.increase_quantity = AsyncMock(return_value=increased_item)

    async with patch_uow(uow):
        response = await async_client.post(
            "/api/v1/orders",
            headers={"Authorization": f"Bearer {access_token}"},
            cookies={"cart_session_id": "s" * 32},
            json={
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "patronymic": "Ivanovych",
                "phone_number": "0961234567",
                "email": "test@example.com",
                "address": "Kyiv, st. 1",
                "shipping_method": "nova_poshta",
                "payment_method": "cash",
            },
        )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["id"] == 100
    assert uow.cart.delete.await_count == 2


@pytest.mark.asyncio
async def test_create_order_authenticated_user_missing_returns_404(
    async_client,
    mock_uow,
    patch_uow,
):
    token_service = JWTTokenService()
    access_token = await token_service.create_access_token(pk=1, username="user")

    async def _cart_create(*, item_in):
        item_in.id = 1
        item_in.items = []
        return item_in

    uow = mock_uow(
        {
            "users": {"get": None},
            "cart": {"get": None, "create": None},
            "website_settings": {"get_or_none": _default_ws},
        },
    )
    uow.users.get = AsyncMock(side_effect=ItemNotFoundException())
    uow.cart.get = AsyncMock(side_effect=ItemNotFoundException())
    uow.cart.create = AsyncMock(side_effect=_cart_create)

    async with patch_uow(uow):
        response = await async_client.post(
            "/api/v1/orders",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "patronymic": "Ivanovych",
                "phone_number": "0961234567",
                "email": "test@example.com",
                "address": "Kyiv, st. 1",
                "shipping_method": "nova_poshta",
                "payment_method": "cash",
            },
        )

    assert response.status_code == 404


# ==================== Customers ====================


@pytest.mark.asyncio
async def test_get_customers_list_success(
    async_client, mock_uow, patch_uow, patch_superuser,
):
    uow = mock_uow({
        "order": {
            "get_customers": [
                type(
                    "Row", (), {
                        "phone_number": "0961234567",
                        "first_name": "Ivan",
                        "last_name": "Ivanov",
                        "patronymic": "Ivanovych",
                        "email": "ivan@test.com",
                        "user_id": 1,
                        "orders_count": 3,
                        "total_spent": 1500,
                        "last_order_at": "2026-04-20T10:00:00",
                    },
                )(),
            ], "get_customers_count": 1,
        },
    })

    async with patch_uow(uow), patch_superuser():
        response = await async_client.get("/api/v1/orders/customers")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["pagination"]["total"] == 1
    assert len(payload["items"]) == 1
    item = payload["items"][0]
    assert item["phone_number"] == "0961234567"
    assert item["first_name"] == "Ivan"
    assert item["last_name"] == "Ivanov"
    assert item["is_registered"] is True
    assert item["orders_count"] == 3


@pytest.mark.asyncio
async def test_get_customers_list_with_text_search(
    async_client, mock_uow, patch_uow, patch_superuser,
):
    uow = mock_uow({"order": {"get_customers": [], "get_customers_count": 0}})

    async with patch_uow(uow), patch_superuser():
        response = await async_client.get("/api/v1/orders/customers?text=Ivan")

    assert response.status_code == 200
    uow.order.get_customers.assert_awaited_once()
    call_kwargs = uow.order.get_customers.await_args.kwargs
    assert call_kwargs["text"] == "Ivan"


@pytest.mark.asyncio
async def test_get_customers_list_with_filters(
    async_client, mock_uow, patch_uow, patch_superuser,
):
    uow = mock_uow({"order": {"get_customers": [], "get_customers_count": 0}})

    async with patch_uow(uow), patch_superuser():
        response = await async_client.get(
            "/api/v1/orders/customers?is_registered=true&date_from=2026-01-01&date_to=2026-12-31",
        )

    assert response.status_code == 200
    call_kwargs = uow.order.get_customers.await_args.kwargs
    assert call_kwargs["is_registered"] == "true"
    assert call_kwargs["date_from"] == "2026-01-01"
    assert call_kwargs["date_to"] == "2026-12-31"


@pytest.mark.asyncio
async def test_get_customers_list_with_sorting(
    async_client, mock_uow, patch_uow, patch_superuser,
):
    uow = mock_uow({"order": {"get_customers": [], "get_customers_count": 0}})

    async with patch_uow(uow), patch_superuser():
        response = await async_client.get(
            "/api/v1/orders/customers?field=orders_count&ordering=desc",
        )

    assert response.status_code == 200
    call_kwargs = uow.order.get_customers.await_args.kwargs
    assert call_kwargs["order_by"] == "orders_count"
    assert call_kwargs["ordering"] == "desc"


@pytest.mark.asyncio
async def test_get_customers_list_unauthorized(async_client):
    response = await async_client.get("/api/v1/orders/customers")
    assert response.status_code == 401
