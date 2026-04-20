import pytest
from tests.factories.messages import MessageFactory


@pytest.mark.asyncio
async def test_get_messages_list_success_default_params(
    async_client,
    mock_uow,
    patch_uow,
    patch_superuser,
):
    msg = MessageFactory.build(id=1, status="new")
    uow = mock_uow({"messages": {"all": [msg], "count": 1}})

    async with patch_uow(uow), patch_superuser():
        response = await async_client.get("/api/v1/messages/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["pagination"] == {"offset": 0, "limit": 20, "total": 1}
    assert payload["data"]["items"][0]["id"] == 1
    assert payload["data"]["items"][0]["status"] == "new"

    uow.messages.count.assert_awaited_once()
    uow.messages.all.assert_awaited_once()
    assert uow.messages.all.await_args.kwargs["order_by"] == ["-created_at"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("field", "ordering", "expected_order_by"),
    [
        ("user_name", "asc", ["user_name"]),
        ("status", "desc", ["-status"]),
    ],
)
async def test_get_messages_list_success_with_sorting(
    async_client,
    mock_uow,
    patch_uow,
    patch_superuser,
    field,
    ordering,
    expected_order_by,
):
    msg = MessageFactory.build(id=1, status="new")
    uow = mock_uow({"messages": {"all": [msg], "count": 1}})

    async with patch_uow(uow), patch_superuser():
        response = await async_client.get(f"/api/v1/messages/?field={field}&ordering={ordering}")

    assert response.status_code == 200
    uow.messages.all.assert_awaited_once()
    assert uow.messages.all.await_args.kwargs["order_by"] == expected_order_by


@pytest.mark.asyncio
async def test_get_messages_list_success_with_filters(
    async_client,
    mock_uow,
    patch_uow,
    patch_superuser,
):
    msgs = [
        MessageFactory.build(id=1, status="read", message="Call me"),
        MessageFactory.build(id=2, status="new", message="Call me"),
    ]
    uow = mock_uow({"messages": {"all": msgs, "count": 1}})

    async with patch_uow(uow), patch_superuser():
        response = await async_client.get(
            "/api/v1/messages/?status=read&text=Call",
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["pagination"]["total"] == 1
    assert payload["data"]["items"][0]["id"] == 1

    uow.messages.count.assert_awaited_once_with(status="read", text="Call")
    assert uow.messages.all.await_args.kwargs["filters"] == {
        "status": "read",
        "text": "Call",
    }


@pytest.mark.asyncio
async def test_get_messages_list_success_with_text_only(
    async_client,
    mock_uow,
    patch_uow,
    patch_superuser,
):
    msg = MessageFactory.build(id=1, status="new", message="димохід нержавійка")
    uow = mock_uow({"messages": {"all": [msg], "count": 1}})

    async with patch_uow(uow), patch_superuser():
        response = await async_client.get("/api/v1/messages/?text=димохід")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["items"][0]["id"] == 1

    uow.messages.count.assert_awaited_once_with(status=None, text="димохід")
    assert uow.messages.all.await_args.kwargs["filters"] == {
        "status": None,
        "text": "димохід",
    }


@pytest.mark.asyncio
async def test_get_messages_list_text_search_with_sorting(
    async_client,
    mock_uow,
    patch_uow,
    patch_superuser,
):
    msgs = [
        MessageFactory.build(id=1, status="new", message="труба одностінна"),
        MessageFactory.build(id=2, status="new", message="одностінна труба"),
    ]
    uow = mock_uow({"messages": {"all": msgs, "count": 2}})

    async with patch_uow(uow), patch_superuser():
        response = await async_client.get(
            "/api/v1/messages/?text=труба одностінна&field=created_at&ordering=desc",
        )

    assert response.status_code == 200
    assert uow.messages.all.await_args.kwargs["filters"] == {
        "status": None,
        "text": "труба одностінна",
    }
    assert uow.messages.all.await_args.kwargs["order_by"] == ["-created_at"]


@pytest.mark.asyncio
async def test_get_messages_list_empty(
    async_client, mock_uow, patch_uow, patch_superuser,
):
    uow = mock_uow({"messages": {"all": [], "count": 0}})

    async with patch_uow(uow), patch_superuser():
        response = await async_client.get("/api/v1/messages/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["items"] == []
    assert payload["data"]["pagination"]["total"] == 0


@pytest.mark.asyncio
async def test_get_messages_list_validation_error_invalid_status(
    async_client,
    mock_uow,
    patch_uow,
    patch_superuser,
):
    uow = mock_uow({"messages": {"all": [], "count": 0}})
    async with patch_uow(uow), patch_superuser():
        response = await async_client.get("/api/v1/messages/?status=invalid")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_messages_list_validation_error_limit_too_big(
    async_client,
    mock_uow,
    patch_uow,
    patch_superuser,
):
    uow = mock_uow({"messages": {"all": [], "count": 0}})
    async with patch_uow(uow), patch_superuser():
        response = await async_client.get("/api/v1/messages/?limit=999")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_messages_list_validation_error_invalid_ordering(
    async_client,
    mock_uow,
    patch_uow,
    patch_superuser,
):
    uow = mock_uow({"messages": {"all": [], "count": 0}})
    async with patch_uow(uow), patch_superuser():
        response = await async_client.get("/api/v1/messages/?ordering=invalid")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_message_success(async_client, mock_uow, patch_uow, patch_superuser):
    msg = MessageFactory.build(id=1, status="new")
    uow = mock_uow({"messages": {"get": msg}})

    async with patch_uow(uow), patch_superuser():
        response = await async_client.get("/api/v1/messages/1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["id"] == 1
    assert payload["data"]["status"] == "new"
    uow.messages.get.assert_awaited_once_with(id=1)


@pytest.mark.asyncio
async def test_create_message_success(async_client, mock_uow, patch_uow):
    message_in = {
        "user_name": "Ivan",
        "phone_number": "0991234567",
        "message": "<b>hi</b>",
    }
    escaped_message = "&lt;b&gt;hi&lt;/b&gt;"
    msg = MessageFactory.build(
        id=1,
        user_name=message_in["user_name"],
        phone_number=message_in["phone_number"],
        message=message_in["message"],
        status="new",
    )
    uow = mock_uow({"messages": {"create": msg}})

    async with patch_uow(uow):
        response = await async_client.post("/api/v1/messages/", json=message_in)

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["id"] == 1
    assert payload["data"]["user_name"] == message_in["user_name"]
    assert payload["data"]["phone_number"] == message_in["phone_number"]
    assert payload["data"]["message"] == escaped_message
    assert payload["data"]["status"] == "new"
    assert "created_at" in payload["data"]

    uow.messages.create.assert_awaited_once()
    created_item = uow.messages.create.await_args.kwargs["item_in"]
    assert created_item.user_name == message_in["user_name"]
    assert created_item.phone_number == message_in["phone_number"]
    assert created_item.message == escaped_message


@pytest.mark.asyncio
async def test_create_message_success_without_message(
    async_client, mock_uow, patch_uow,
):
    message_in = {
        "user_name": "Ivan",
        "phone_number": "0991234567",
    }
    msg = MessageFactory.build(
        id=1,
        user_name=message_in["user_name"],
        phone_number=message_in["phone_number"],
        message=None,
        status="new",
    )
    uow = mock_uow({"messages": {"create": msg}})

    async with patch_uow(uow):
        response = await async_client.post("/api/v1/messages/", json=message_in)

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["message"] is None


@pytest.mark.asyncio
async def test_create_message_validation_error_invalid_phone(
    async_client, patch_uow, mock_uow,
):
    uow = mock_uow({"messages": {"create": None}})
    async with patch_uow(uow):
        response = await async_client.post(
            "/api/v1/messages/",
            json={"user_name": "Ivan", "phone_number": "09A123456"},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_message_validation_error_invalid_user_name(
    async_client, patch_uow, mock_uow,
):
    uow = mock_uow({"messages": {"create": None}})
    async with patch_uow(uow):
        response = await async_client.post(
            "/api/v1/messages/",
            json={"user_name": "Ivan!!", "phone_number": "0991234567"},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_message_validation_error_message_too_long(
    async_client, patch_uow, mock_uow,
):
    uow = mock_uow({"messages": {"create": None}})
    async with patch_uow(uow):
        response = await async_client.post(
            "/api/v1/messages/",
            json={
                "user_name": "Ivan",
                "phone_number": "0991234567",
                "message": "a" * 1001,
            },
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_message_success(
    async_client, mock_uow, patch_uow, patch_superuser,
):
    uow = mock_uow({"messages": {"delete": None}})

    async with patch_uow(uow), patch_superuser():
        response = await async_client.delete("/api/v1/messages/1")

    assert response.status_code == 200
    assert response.content in (b"", b"null")
    uow.messages.delete.assert_awaited_once_with(id=1)


@pytest.mark.asyncio
async def test_change_message_status_success(
    async_client,
    mock_uow,
    patch_uow,
    patch_superuser,
):
    msg = MessageFactory.build(id=1, status="read")
    uow = mock_uow({"messages": {"update": msg}})

    async with patch_uow(uow), patch_superuser():
        response = await async_client.patch(
            "/api/v1/messages/change-status/1",
            json={"status": "read"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["id"] == 1
    assert payload["data"]["status"] == "read"

    uow.messages.update.assert_awaited_once()
    assert uow.messages.update.await_args.kwargs["id"] == 1
