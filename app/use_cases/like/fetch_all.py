from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.services.likes import AbstractLikeService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchLikesUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        user_id: int,
        uow: AbstractUnitOfWork,
    ) -> list[int]: ...


@dataclass
class FetchLikesUseCase(AbstractFetchLikesUseCase):
    like_service: AbstractLikeService

    async def execute(
        self,
        user_id: int,
        uow: AbstractUnitOfWork,
    ) -> list[int]:
        async with uow:
            return await self.like_service.get_ids_list(
                user_id=user_id,
                uow=uow,
            )
