from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.likes import CreateLikeSchema, ReadLikeSchema
from app.services.likes import AbstractLikeService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractCreateLikeUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        like_in: CreateLikeSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadLikeSchema: ...


@dataclass
class CreateLikeUseCase(AbstractCreateLikeUseCase):
    like_service: AbstractLikeService

    async def execute(
        self,
        like_in: CreateLikeSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadLikeSchema:
        async with uow:
            return await self.like_service.create(
                item_in=like_in,
                uow=uow,
            )
