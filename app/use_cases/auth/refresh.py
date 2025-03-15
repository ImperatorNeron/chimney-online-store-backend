from dataclasses import dataclass

from app.schemas.tokens import TokenInfoSchema
from app.schemas.users import ReadUserSchema
from app.services.tokens import AbstractJWTTokenService


@dataclass
class RefreshTokenUseCase:

    token_service: AbstractJWTTokenService

    async def execute(
        self,
        user: ReadUserSchema,
    ) -> TokenInfoSchema:
        return TokenInfoSchema(
            access_token=await self.token_service.create_access_token(
                pk=user.id,
                username=user.username,
            ),
        )
