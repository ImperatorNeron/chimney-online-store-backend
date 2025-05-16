from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.services.likes import AbstractLikeService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractDeleteLikeUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        product_id: int,
        user_id: int,
        uow: AbstractUnitOfWork,
    ) -> None: ...


@dataclass
class DeleteLikeUseCase(AbstractDeleteLikeUseCase):
    like_service: AbstractLikeService

    async def execute(
        self,
        product_id: int,
        user_id: int,
        uow: AbstractUnitOfWork,
    ) -> None:
        async with uow:
            return await self.like_service.delete(
                product_id=product_id,
                user_id=user_id,
                uow=uow,
            )
