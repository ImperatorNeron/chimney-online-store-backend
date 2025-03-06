import pytest
from tests.factories.users import AuthUserPayloadFactory


@pytest.fixture
async def auth_user_payload():
    return AuthUserPayloadFactory()
