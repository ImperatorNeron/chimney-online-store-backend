import pytest
from tests.factories.likes import LikeFactory
from tests.factories.users import ReadUserFactory


@pytest.mark.asyncio
async def test_get_likes_list_success(
    async_client, mock_uow, patch_uow, patch_auth_user,
):
    auth_user = ReadUserFactory.build(id=1)
    fake_models = [
        LikeFactory.build(id=1, user_id=1, product_id=101),
        LikeFactory.build(id=2, user_id=1, product_id=202),
    ]
    uow = mock_uow({"like": {"all": fake_models}})

    async with patch_uow(uow), patch_auth_user(auth_user):
        response = await async_client.get("/api/v1/like")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"] == [101, 202]
    assert uow.like.all.await_args.kwargs["filters"] == {"user_id": 1}


@pytest.mark.asyncio
async def test_get_likes_list_blocked_without_user(async_client):
    response = await async_client.get("/api/v1/like")

    assert response.status_code == 401
    payload = response.json()
    assert payload["data"] is None
    assert payload["errors"][0]["code"] == "invalid_token"


@pytest.mark.asyncio
async def test_create_like_success(async_client, mock_uow, patch_uow, patch_auth_user):
    auth_user = ReadUserFactory.build(id=1)
    like_model = LikeFactory.build(id=1, user_id=1, product_id=123)
    uow = mock_uow({"like": {"get_or_none": None, "create": like_model}})

    async with patch_uow(uow), patch_auth_user(auth_user):
        response = await async_client.post("/api/v1/like?product_id=123")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["id"] == 1
    assert payload["data"]["user_id"] == 1
    assert payload["data"]["product_id"] == 123

    uow.like.get_or_none.assert_awaited_once_with(user_id=1, product_id=123)
    uow.like.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_like_conflict_already_exists(
    async_client, mock_uow, patch_uow, patch_auth_user,
):
    auth_user = ReadUserFactory.build(id=1)
    existing_like = LikeFactory.build(id=10, user_id=1, product_id=123)
    uow = mock_uow({"like": {"get_or_none": existing_like, "create": None}})

    async with patch_uow(uow), patch_auth_user(auth_user):
        response = await async_client.post("/api/v1/like?product_id=123")

    assert response.status_code == 409
    payload = response.json()
    assert payload["data"] is None
    assert payload["errors"][0]["code"] == "already_exists"
    uow.like.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_like_success(async_client, mock_uow, patch_uow, patch_auth_user):
    auth_user = ReadUserFactory.build(id=1)
    uow = mock_uow({"like": {"delete": None}})

    async with patch_uow(uow), patch_auth_user(auth_user):
        response = await async_client.delete("/api/v1/like/123")

    assert response.status_code == 200
    payload = response.json()
    assert "data" in payload
    assert payload["data"] is None
    uow.like.delete.assert_awaited_once_with(product_id=123, user_id=1)
