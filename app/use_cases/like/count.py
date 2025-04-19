from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.services.likes import AbstractLikeService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractCountUserLikesUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        user_id: int,
        uow: AbstractUnitOfWork,
    ) -> int: ...


@dataclass
class CountUserLikesUseCase(AbstractCountUserLikesUseCase):
    like_service: AbstractLikeService

    async def execute(
        self,
        user_id: int,
        uow: AbstractUnitOfWork,
    ) -> int:
        async with uow:
            return await self.like_service.count(
                user_id=user_id,
                uow=uow,
            )
