from app.exceptions.auth import InvalidCredentialsError
from app.schemas.tokens import TokenInfoSchema
from app.schemas.users import LoginUserSchema
from app.use_cases.auth.common import BaseAuthUseCase
from app.utils.unit_of_work import AbstractUnitOfWork


class LoginUserUseCase(BaseAuthUseCase):

    async def execute(
        self,
        uow: AbstractUnitOfWork,
        user_in: LoginUserSchema,
    ) -> TokenInfoSchema:
        async with uow:
            user = await self._fetch_user_by_username(
                uow=uow,
                username=user_in.username,
            )

            if not self._is_valid_password(
                user_in.password,
                user.hashed_password,
            ):
                raise InvalidCredentialsError()

            return await self._generate_tokens_info(
                pk=user.id,
                username=user.username,
            )
