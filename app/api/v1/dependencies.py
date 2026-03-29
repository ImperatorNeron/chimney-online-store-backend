import logging
import secrets
from typing import Annotated

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
from app.core.settings import settings
from app.schemas.carts import BaseCartSchema, CreateCartSchema, ReadFullCartSchema
from app.schemas.users import ReadUserSchema
from app.services.tokens import AbstractJWTTokenService
from app.services.users import AbstractUserService
from app.use_cases.cart.create import AbstractCreateCartUseCase
from app.use_cases.cart.fetch import AbstractFetchCartUseCase
from app.use_cases.cart.merge import AbstractMergeCartsUseCase
from app.utils.unit_of_work import AbstractUnitOfWork, UnitOfWork


logger = logging.getLogger(__name__)

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
    except InvalidTokenError as e:
        logger.warning("Invalid token: %s", e)
        raise InvalidTokenException()
    return payload


async def validate_token_type(
    payload: dict,
    current_token_type: str,
) -> None:
    jwt_token_type = payload.get("token_type")

    if jwt_token_type != current_token_type:
        logger.warning(
            "Token type mismatch: expected '%s', got '%s'",
            current_token_type,
            jwt_token_type,
        )
        raise InvalidTokenTypeException()


async def get_user_by_token_sub(
    container: Container,
    uow: AbstractUnitOfWork,
    payload: dict,
) -> ReadUserSchema:
    service: AbstractUserService = container.resolve(AbstractUserService)
    async with uow:
        user = await service.get_one(
            uow=uow, conditions={"id": int(payload.get("sub"))},
        )
    if user is None:
        logger.warning("User not found with id: %s", payload.get("sub"))
        raise UserNotFoundException()
    return ReadUserSchema(**user.model_dump(exclude="hashed_password"))


async def get_auth_user_from_token_of_type(
    payload: dict,
    token_type: str,
    container: Container,
    uow: AbstractUnitOfWork,
):
    await validate_token_type(payload=payload, current_token_type=token_type)
    return await get_user_by_token_sub(
        container=container,
        uow=uow,
        payload=payload,
    )


async def get_auth_from_access_token(
    payload: Annotated[dict, Depends(get_current_token_payload)],
    container: Annotated[Container, Depends(get_container)],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
) -> ReadUserSchema:
    return await get_auth_user_from_token_of_type(
        payload=payload,
        token_type="access",
        container=container,
        uow=uow,
    )


async def get_current_auth_user_for_refresh(
    request: Request,
    container: Annotated[Container, Depends(get_container)],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
):
    refresh_token = request.cookies.get("refresh_token")
    payload = await get_current_token_payload(container=container, token=refresh_token)
    return await get_auth_user_from_token_of_type(
        payload=payload,
        token_type="refresh",
        container=container,
        uow=uow,
    )


async def get_current_active_auth_user(
    user: Annotated[ReadUserSchema, Depends(get_auth_from_access_token)],
):
    if user.is_active:
        return user
    raise InactiveUserException()


async def get_current_active_auth_superuser(
    user: Annotated[ReadUserSchema, Depends(get_current_active_auth_user)],
):
    if user.is_superuser:
        return user
    # TODO: change all user errors and clearify whole users major
    raise UserAdminPermissionException()


async def get_user_or_none(
    token: Annotated[str, Depends(oauth2_scheme)],
    container: Annotated[Container, Depends(get_container)],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
):
    try:
        user = await get_auth_user_from_token_of_type(
            payload=await get_current_token_payload(container=container, token=token),
            token_type="access",
            container=container,
            uow=uow,
        )
        return user.id
    except (InvalidTokenTypeException, InvalidTokenException) as e:
        logger.info("No valid user from token: %s", str(e))


async def refresh_check(
    request: Request,
    container: Annotated[Container, Depends(get_container)],
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return {"is_authenticated": False}

    try:
        # Перевірити токен, наприклад, через JWT decode або бібліотеку
        await get_current_token_payload(container=container, token=refresh_token)
        return {"is_authenticated": True}
    except InvalidTokenException:
        return {"is_authenticated": False}


###################################################


def set_session_cookie(response: Response, session_id: str) -> None:
    response.set_cookie(
        key=settings.session.session_key,
        value=session_id,
        max_age=settings.session.session_expire_seconds,
        httponly=settings.session.session_httponly,
        secure=settings.session.session_secure,
        samesite=settings.session.same_site,
    )


async def _get_user_cart_or_create_new(
    uow: AbstractUnitOfWork,
    fetch_cart: AbstractFetchCartUseCase,
    create_cart: AbstractCreateCartUseCase,
    cart_identifiers: BaseCartSchema,
) -> ReadFullCartSchema:
    try:
        return await fetch_cart.execute(uow=uow, cart_identifiers=cart_identifiers)
    except ItemNotFoundException:
        logger.info(
            "Cart not found, creating new one: %s", cart_identifiers.model_dump(),
        )
        cart = await create_cart.execute(
            uow=uow,
            cart_in=CreateCartSchema(**cart_identifiers.model_dump()),
        )
        return ReadFullCartSchema(
            **cart.model_dump(exclude={"items"}),
            items=[],
            total_price=0,
            total_quantity=0,
        )


async def _create_anonymous_cart(
    response: Response,
    uow: AbstractUnitOfWork,
    create_cart: AbstractCreateCartUseCase,
):
    session_id = secrets.token_urlsafe(settings.session.urlsafe_token_length)
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
        logger.info("No cart session found, creating new cart")
        return await _create_anonymous_cart(
            response=response,
            uow=uow,
            create_cart=create_cart,
        )
    try:
        return await fetch_cart.execute(
            uow=uow, cart_identifiers=BaseCartSchema(session_id=session_id),
        )
    except ItemNotFoundException:
        logger.info("Session cart not found, creating new one and deleting old cookie")
        response.delete_cookie(
            key="cart_session_id",
            secure=settings.session.session_secure,
            httponly=settings.session.session_httponly,
            samesite=settings.session.same_site,
        )
        return await _create_anonymous_cart(
            response=response,
            uow=uow,
            create_cart=create_cart,
        )


async def get_user_cart(
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
            cart_identifiers=BaseCartSchema(user_id=int(payload.get("sub"))),
        )

        if session_id:
            # TODO: додати обробку можливих помилок
            # TODO: всередині приймати не **kwargs а нормальні значення session_id or user_id
            session_cart = await fetch_cart.execute(
                uow=uow, cart_identifiers=BaseCartSchema(session_id=session_id),
            )
            user_cart = await merge_carts.execute(
                user_cart=user_cart,
                session_cart=session_cart,
                uow=uow,
            )
            response.delete_cookie(
                "cart_session_id",
                secure=settings.session.session_secure,
                httponly=settings.session.session_httponly,
                samesite=settings.session.same_site,
            )
        return user_cart
    return await handle_anonymous_cart(
        request=request,
        response=response,
        uow=uow,
        create_cart=create_cart,
        fetch_cart=fetch_cart,
    )
