from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.categories import CreateCategorySchema, ReadCategorySchema
from app.services.categories import AbstractCategoryService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractCreateCategoryUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        category_in: CreateCategorySchema,
        uow: AbstractUnitOfWork,
    ) -> ReadCategorySchema: ...


@dataclass
class CreateCategoryUseCase(AbstractCreateCategoryUseCase):

    categoty_service: AbstractCategoryService

    async def execute(
        self,
        category_in: CreateCategorySchema,
        uow: AbstractUnitOfWork,
    ):
        async with uow:
            return await self.categoty_service.create(
                category_in=category_in,
                uow=uow,
            )
