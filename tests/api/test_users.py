import pytest
from tests.factories.users import ReadUserFactory, UserFactory


@pytest.mark.asyncio
async def test_get_authenticated_user_profile_success(async_client, patch_auth_user):
    auth_user = ReadUserFactory.build(id=1, username="testuser")

    async with patch_auth_user(auth_user):
        response = await async_client.get("/api/v1/users/me")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == 1
    assert payload["username"] == "testuser"
    assert "hashed_password" not in payload


@pytest.mark.asyncio
async def test_update_authenticated_user_profile_success(
    async_client,
    mock_uow,
    patch_uow,
    patch_auth_user,
):
    auth_user = ReadUserFactory.build(id=1, username="testuser")
    updated_user = UserFactory.build(
        id=1,
        username="testuser",
        first_name="John",
        last_name="Doe",
    )
    uow = mock_uow({"users": {"update": updated_user}})

    async with patch_uow(uow), patch_auth_user(auth_user):
        response = await async_client.patch(
            "/api/v1/users/me/update",
            json={"first_name": "John", "last_name": "Doe"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["id"] == 1
    assert payload["data"]["username"] == "testuser"
    assert payload["data"]["first_name"] == "John"
    assert payload["data"]["last_name"] == "Doe"
    assert "hashed_password" not in payload["data"]

    uow.users.update.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_authenticated_user_profile_validation_error_password_without_confirm(
    async_client,
    mock_uow,
    patch_uow,
    patch_auth_user,
):
    auth_user = ReadUserFactory.build(id=1)
    uow = mock_uow({"users": {"update": None}})

    async with patch_uow(uow), patch_auth_user(auth_user):
        response = await async_client.patch(
            "/api/v1/users/me/update",
            json={"password": "Secret123"},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_authenticated_user_profile_validation_error_password_mismatch(
    async_client,
    mock_uow,
    patch_uow,
    patch_auth_user,
):
    auth_user = ReadUserFactory.build(id=1)
    uow = mock_uow({"users": {"update": None}})

    async with patch_uow(uow), patch_auth_user(auth_user):
        response = await async_client.patch(
            "/api/v1/users/me/update",
            json={"password": "Secret123", "confirm_password": "Secret321"},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_authenticated_user_profile_conflict_email_exists(
    async_client,
    mock_uow,
    patch_uow,
    patch_auth_user,
):
    auth_user = ReadUserFactory.build(id=1)
    other_user = UserFactory.build(id=2, email="other@example.com")
    uow = mock_uow({"users": {"get_or_none": other_user, "update": None}})

    async with patch_uow(uow), patch_auth_user(auth_user):
        response = await async_client.patch(
            "/api/v1/users/me/update",
            json={"email": "other@example.com"},
        )

    assert response.status_code == 409
    payload = response.json()
    assert payload["data"] is None
    assert payload["errors"][0]["code"] == "email_exists"
    uow.users.update.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_authenticated_user_profile_conflict_phone_number_exists(
    async_client,
    mock_uow,
    patch_uow,
    patch_auth_user,
):
    auth_user = ReadUserFactory.build(id=1)
    other_user = UserFactory.build(id=2, phone_number="0961234567")
    uow = mock_uow({"users": {"get_or_none": other_user, "update": None}})

    async with patch_uow(uow), patch_auth_user(auth_user):
        response = await async_client.patch(
            "/api/v1/users/me/update",
            json={"phone_number": "0961234567"},
        )

    assert response.status_code == 409
    payload = response.json()
    assert payload["data"] is None
    assert payload["errors"][0]["code"] == "phone_number_exists"
    uow.users.update.assert_not_awaited()
