from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.categories import ReadCategorySchema, UpdateCategorySchema
from app.services.categories import AbstractCategoryService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractUpdateCategoryUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        category_id: int,
        category_in: UpdateCategorySchema,
        uow: AbstractUnitOfWork,
    ) -> ReadCategorySchema: ...


@dataclass
class UpdateCategoryUseCase(AbstractUpdateCategoryUseCase):

    category_service: AbstractCategoryService

    async def execute(
        self,
        category_id: int,
        category_in: UpdateCategorySchema,
        uow: AbstractUnitOfWork,
    ):
        async with uow:
            return await self.category_service.update(
                category_id=category_id,
                category_in=category_in,
                uow=uow,
            )
