from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.likes import ReadLikeSchema
from app.services.likes import AbstractLikeService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchLikesUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        user_id: int,
        uow: AbstractUnitOfWork,
    ) -> list[ReadLikeSchema]: ...


@dataclass
class FetchLikesUseCase(AbstractFetchLikesUseCase):
    like_service: AbstractLikeService

    async def execute(
        self,
        user_id: int,
        uow: AbstractUnitOfWork,
    ) -> list[ReadLikeSchema]:
        async with uow:
            return await self.like_service.fetch_all(user_id=user_id, uow=uow)
