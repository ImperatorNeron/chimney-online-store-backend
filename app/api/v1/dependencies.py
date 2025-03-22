import secrets
from typing import Annotated, Any, Callable

from fastapi import Depends, Request, Response
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from jwt import InvalidTokenError
from punq import Container

from app.core.containers import get_container
from app.core.exceptions.common import (
    InactiveUserException,
    InvalidTokenException,
    InvalidTokenTypeException,
    ItemNotFoundException,
    UserAdminPermissionException,
    UserNotFoundException,
)
from app.schemas.carts import CreateCartSchema, ReadFullCartSchema
from app.schemas.users import ReadUserSchema
from app.services.tokens import AbstractJWTTokenService
from app.services.users import AbstractUserService
from app.use_cases.cart.create import AbstractCreateCartUseCase
from app.use_cases.cart.fetch import AbstractFetchCartUseCase
from app.use_cases.cart.merge import AbstractMergeCartsUseCase
from app.utils.unit_of_work import AbstractUnitOfWork, UnitOfWork


http_bearer = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login/",
    auto_error=False,
)


async def get_current_token_payload(
    container: Annotated[Container, Depends(get_container)],
    token: Annotated[str, Depends(oauth2_scheme)],
):
    try:
        service: AbstractJWTTokenService = container.resolve(AbstractJWTTokenService)
        payload = await service.decode_jwt(token=token)
    # TODO: think about login end
    except InvalidTokenError:
        raise InvalidTokenException()
    return payload


async def validate_token_type(
    payload: dict,
    current_token_type: str,
) -> None:
    jwt_token_type = payload.get("token_type")

    if jwt_token_type != current_token_type:
        raise InvalidTokenTypeException()


async def get_user_by_token_sub(
    container: Container,
    uow: AbstractUnitOfWork,
    payload: dict,
) -> ReadUserSchema:
    service: AbstractUserService = container.resolve(AbstractUserService)
    user = await service.get_user_by_id(uow=uow, id=int(payload.get("sub")))
    if user is None:
        raise UserNotFoundException()
    return ReadUserSchema(**user.model_dump(exclude="hashed_password"))


def get_auth_user_from_token_of_type(token_type: str) -> Callable:
    async def get_auth_user_from_token(
        payload: Annotated[dict, Depends(get_current_token_payload)],
        container: Annotated[Container, Depends(get_container)],
        uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    ) -> ReadUserSchema:
        await validate_token_type(payload=payload, current_token_type=token_type)
        return await get_user_by_token_sub(
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
    raise InactiveUserException()


async def get_current_active_auth_superuser(
    user: Annotated[ReadUserSchema, Depends(get_current_auth_user)],
):
    if user.is_active and user.is_superuser:
        return user
    # TODO: change all user errors and clearify whole users major
    raise UserAdminPermissionException()


###################################################


def set_session_cookie(response: Response, session_id: str) -> None:
    response.set_cookie(
        key="cart_session_id",
        value=session_id,
        max_age=30 * 24 * 3600,
        httponly=True,
        secure=True,
        samesite="Lax",
    )


async def _get_user_cart_or_create_new(
    uow: AbstractUnitOfWork,
    fetch_cart: AbstractFetchCartUseCase,
    create_cart: AbstractCreateCartUseCase,
    **cart_data: Any,
) -> ReadFullCartSchema:
    print(cart_data)
    try:
        return await fetch_cart.execute(uow=uow, **cart_data)
    except ItemNotFoundException:
        cart = await create_cart.execute(
            uow=uow,
            cart_in=CreateCartSchema(**cart_data),
        )
        return ReadFullCartSchema(
            **cart.model_dump(),
            items=[],
            total_price=0,
            total_quantity=0,
        )


async def _create_anonymous_cart(
    response: Response,
    uow: AbstractUnitOfWork,
    create_cart: AbstractCreateCartUseCase,
    session_id: str,
):
    # TODO: замінити скрізь на 32 байти = 43 символи
    session_id = secrets.token_urlsafe(27)
    set_session_cookie(response=response, session_id=session_id)
    cart = await create_cart.execute(
        uow=uow,
        cart_in=CreateCartSchema(session_id=session_id),
    )
    return ReadFullCartSchema(
        **cart.model_dump(exclude={"items"}),
        items=[],
        total_price=0,
        total_quantity=0,
    )


async def handle_anonymous_cart(
    request: Request,
    response: Response,
    uow: AbstractUnitOfWork,
    fetch_cart: AbstractFetchCartUseCase,
    create_cart: AbstractCreateCartUseCase,
):
    session_id = request.cookies.get("cart_session_id")

    if not session_id:
        return await _create_anonymous_cart(
            response=response,
            uow=uow,
            create_cart=create_cart,
            session_id=session_id,
        )
    try:
        return await fetch_cart.execute(uow=uow, session_id=session_id)
    except ItemNotFoundException:
        response.delete_cookie(key="cart_session_id")
        return await _create_anonymous_cart(
            response=response,
            uow=uow,
            create_cart=create_cart,
            session_id=session_id,
        )


async def get_cart(
    request: Request,
    response: Response,
    container: Annotated[Container, Depends(get_container)],
    token: Annotated[str, Depends(oauth2_scheme)],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    fetch_cart: Annotated[
        AbstractFetchCartUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchCartUseCase)),
    ],
    create_cart: Annotated[
        AbstractCreateCartUseCase,
        Depends(lambda: get_container().resolve(AbstractCreateCartUseCase)),
    ],
    merge_carts: Annotated[
        AbstractMergeCartsUseCase,
        Depends(lambda: get_container().resolve(AbstractMergeCartsUseCase)),
    ],
) -> ReadFullCartSchema:

    session_id = request.cookies.get("cart_session_id")

    if token:
        payload = await get_current_token_payload(container=container, token=token)
        await validate_token_type(payload=payload, current_token_type="access")
        user_cart = await _get_user_cart_or_create_new(
            uow=uow,
            fetch_cart=fetch_cart,
            create_cart=create_cart,
            user_id=int(payload.get("sub")),
        )

        if session_id:
            # TODO: додати обробку можливих помилок
            session_cart = await fetch_cart.execute(uow=uow, session_id=session_id)
            user_cart = await merge_carts.execute(
                user_cart=user_cart,
                session_cart=session_cart,
                uow=uow,
            )
            response.delete_cookie("cart_session_id")
        return user_cart
    return await handle_anonymous_cart(
        request=request,
        response=response,
        uow=uow,
        create_cart=create_cart,
        fetch_cart=fetch_cart,
    )
