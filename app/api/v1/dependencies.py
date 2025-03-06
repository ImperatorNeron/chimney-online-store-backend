from typing import (
    Annotated,
    Callable,
)

from fastapi import Depends
from fastapi.security import (
    HTTPBearer,
    OAuth2PasswordBearer,
)

from jwt import InvalidTokenError
from punq import Container

from app.core.containers import get_container
from app.exceptions.auth import (
    InvalidJWTTokenError,
    InvalidJWTTokenYypeError,
)
from app.exceptions.users import (
    InactiveUserError,
    UserWasNotFoundError,
)
from app.schemas.users import ReadUserSchema
from app.services.tokens import AbstractJWTTokenService
from app.services.users import AbstractUserService
from app.utils.unit_of_work import (
    AbstractUnitOfWork,
    UnitOfWork,
)


http_bearer = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login/",
)


async def get_current_token_payload(
    container: Annotated[Container, Depends(get_container)],
    token: Annotated[str, Depends(oauth2_scheme)],
):
    try:
        service: AbstractJWTTokenService = container.resolve(AbstractJWTTokenService)
        payload = await service.decode_jwt(token=token)
    except InvalidTokenError as e:
        raise InvalidJWTTokenError(detail=e)
    return payload


async def validate_token_type(
    payload: dict,
    current_token_type: str,
) -> None:
    jwt_token_type = payload.get("token_type")

    if jwt_token_type != current_token_type:
        raise InvalidJWTTokenYypeError(jwt_token_type, current_token_type)


async def get_user_bu_token_sub(
    container: Container,
    uow: AbstractUnitOfWork,
    payload: dict,
) -> ReadUserSchema:
    service: AbstractUserService = container.resolve(AbstractUserService)
    user = await service.get_user_by_id(uow=uow, id=payload.get("sub"))
    if user is None:
        raise UserWasNotFoundError()
    return ReadUserSchema(**user.model_dump(exclude="hashed_password"))


def get_auth_user_from_token_of_type(token_type: str) -> Callable:
    async def get_auth_user_from_token(
        payload: Annotated[dict, Depends(get_current_token_payload)],
        container: Annotated[Container, Depends(get_container)],
        uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    ) -> ReadUserSchema:
        await validate_token_type(payload=payload, current_token_type=token_type)
        return await get_user_bu_token_sub(
            container=container,
            uow=uow,
            payload=payload,
        )

    return get_auth_user_from_token


get_current_auth_user = get_auth_user_from_token_of_type("access")
get_current_auth_user_for_refresh = get_auth_user_from_token_of_type("refresh")


async def get_current_active_auth_user(
    user: Annotated[ReadUserSchema, Depends(get_current_auth_user)],
):
    if user.is_active:
        return user
    raise InactiveUserError()

