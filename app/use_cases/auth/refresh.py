from app.schemas.tokens import TokenInfoSchema
from app.schemas.users import ReadUserSchema
from app.use_cases.auth.common import BaseAuthUseCase


class RefreshTokenUseCase(BaseAuthUseCase):

    async def execute(
        self,
        user: ReadUserSchema,
    ) -> TokenInfoSchema:
        return TokenInfoSchema(
            access_token=await self._generate_access_token(
                pk=user.id,
                username=user.username,
            ),
        )
