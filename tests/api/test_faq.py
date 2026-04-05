import pytest
from tests.factories.faqs import FAQFactory


@pytest.mark.asyncio
async def test_get_faqs_list_success(async_client, mock_uow, patch_uow):
    fake_models = FAQFactory.build_batch(3)

    uow = mock_uow({"faq": {"all": fake_models}})
    async with patch_uow(uow):
        response = await async_client.get("/api/v1/faq")

    assert response.status_code == 200
    payload = response.json()
    assert "data" in payload
    assert len(payload["data"]) == 3
    uow.faq.all.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_faq_success(async_client, mock_uow, patch_uow, patch_superuser):
    fake_model = FAQFactory.build(id=1, youtube_url="https://youtu.be/abc123")

    uow = mock_uow({"faq": {"get": fake_model}})
    async with patch_uow(uow), patch_superuser():
        response = await async_client.get("/api/v1/faq/1")

    assert response.status_code == 200
    payload = response.json()
    assert "data" in payload
    assert payload["data"]["id"] == 1
    assert payload["data"]["question"] == fake_model.question
    assert payload["data"]["answer"] == fake_model.answer
    assert payload["data"]["youtube_url"] == fake_model.youtube_url
    assert payload["data"]["embed_url"] == "https://www.youtube.com/embed/abc123"
    uow.faq.get.assert_awaited_once_with(id=1)


@pytest.mark.asyncio
async def test_create_faq_success(async_client, mock_uow, patch_uow, patch_superuser):
    faq_in = {
        "question": "How to return product?",
        "answer": "Write to support and provide order number.",
        "youtube_url": "https://youtu.be/abc123",
    }
    fake_model = FAQFactory.build(
        id=1,
        question=faq_in["question"],
        answer=faq_in["answer"],
        youtube_url=faq_in["youtube_url"],
    )

    uow = mock_uow({"faq": {"create": fake_model}})
    async with patch_uow(uow), patch_superuser():
        response = await async_client.post("/api/v1/faq", json=faq_in)

    assert response.status_code == 200
    payload = response.json()
    assert "data" in payload
    assert payload["data"]["id"] == 1
    assert payload["data"]["question"] == faq_in["question"]
    assert payload["data"]["answer"] == faq_in["answer"]
    assert payload["data"]["youtube_url"] == faq_in["youtube_url"]
    assert payload["data"]["embed_url"] == "https://www.youtube.com/embed/abc123"
    uow.faq.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_faq_success(async_client, mock_uow, patch_uow, patch_superuser):
    faq_in = {
        "question": "Updated question?",
        "youtube_url": "https://youtu.be/new456",
    }
    fake_model = FAQFactory.build(
        id=1,
        question=faq_in["question"],
        answer="Existing answer stays the same.",
        youtube_url=faq_in["youtube_url"],
    )

    uow = mock_uow({"faq": {"update": fake_model}})
    async with patch_uow(uow), patch_superuser():
        response = await async_client.patch("/api/v1/faq/1", json=faq_in)

    assert response.status_code == 200
    payload = response.json()
    assert "data" in payload
    assert payload["data"]["id"] == 1
    assert payload["data"]["question"] == faq_in["question"]
    assert payload["data"]["answer"] == fake_model.answer
    assert payload["data"]["youtube_url"] == faq_in["youtube_url"]
    assert payload["data"]["embed_url"] == "https://www.youtube.com/embed/new456"

    uow.faq.update.assert_awaited_once()
    assert uow.faq.update.await_args.kwargs["id"] == 1
    updated_item = uow.faq.update.await_args.kwargs["item_in"]
    assert updated_item.question == faq_in["question"]
    assert updated_item.youtube_url == faq_in["youtube_url"]


@pytest.mark.asyncio
async def test_delete_faq_success(async_client, mock_uow, patch_uow, patch_superuser):
    uow = mock_uow({"faq": {"delete": None}})
    async with patch_uow(uow), patch_superuser():
        response = await async_client.delete("/api/v1/faq/1")

    assert response.status_code == 200
    payload = response.json()
    assert "data" in payload
    assert payload["data"] is None
    uow.faq.delete.assert_awaited_once_with(id=1)


@pytest.mark.asyncio
async def test_get_faq_embed_url_none_for_invalid_youtube_url(
    async_client,
    mock_uow,
    patch_uow,
    patch_superuser,
):
    fake_model = FAQFactory.build(id=1, youtube_url="not-a-youtube-url")
    uow = mock_uow({"faq": {"get": fake_model}})

    async with patch_uow(uow), patch_superuser():
        response = await async_client.get("/api/v1/faq/1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["youtube_url"] == "not-a-youtube-url"
    assert payload["data"]["embed_url"] is None


@pytest.mark.asyncio
async def test_create_faq_validation_error_question_too_long(
    async_client,
    mock_uow,
    patch_uow,
    patch_superuser,
):
    uow = mock_uow({"faq": {"create": None}})
    async with patch_uow(uow), patch_superuser():
        response = await async_client.post(
            "/api/v1/faq",
            json={"question": "a" * 256, "answer": "ok"},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_faq_validation_error_question_too_long(
    async_client,
    mock_uow,
    patch_uow,
    patch_superuser,
):
    uow = mock_uow({"faq": {"update": None}})
    async with patch_uow(uow), patch_superuser():
        response = await async_client.patch(
            "/api/v1/faq/1",
            json={"question": "a" * 256},
        )
    assert response.status_code == 422
