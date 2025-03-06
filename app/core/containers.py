from functools import lru_cache

import punq

from app.services.auth import (
    AbstractAuthService,
    AuthService,
)
from app.services.messages import AbstractMessageService, MessageService
from app.services.tokens import (
    AbstractJWTTokenService,
    JWTTokenService,
)
from app.services.users import (
    AbstractUserService,
    UserService,
)
from app.use_cases.auth.login import LoginUserUseCase
from app.use_cases.auth.refresh import RefreshTokenUseCase
from app.use_cases.auth.registration import RegisterUserUseCase
from app.use_cases.messages.create_messages import (
    AbstractCreateMessageUseCase,
    CreateMessageUseCase,
)
from app.use_cases.messages.fetch_message import (
    AbstractFetchMessageUseCase,
    FetchMessageUseCase,
)
from app.use_cases.messages.fetch_messages import (
    AbstractFetchMessagesUseCase,
    FetchMessagesUseCase,
)


@lru_cache(1)
def get_container() -> punq.Container:
    return _initialize_container()


def _initialize_container() -> punq.Container:
    container = punq.Container()

    # Services
    container.register(AbstractAuthService, AuthService)
    container.register(AbstractUserService, UserService)
    container.register(AbstractJWTTokenService, JWTTokenService)
    container.register(AbstractMessageService, MessageService)

    # Use cases
    container.register(RegisterUserUseCase)
    container.register(LoginUserUseCase)
    container.register(RefreshTokenUseCase)
    container.register(AbstractCreateMessageUseCase, CreateMessageUseCase)
    container.register(AbstractFetchMessagesUseCase, FetchMessagesUseCase)
    container.register(AbstractFetchMessageUseCase, FetchMessageUseCase)

    return container
