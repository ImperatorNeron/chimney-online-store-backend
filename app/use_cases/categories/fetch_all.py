from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.categories import ReadCategorySchema
from app.services.categories import AbstractCategoryService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchCategoriesUseCase(ABC):

    @abstractmethod
    async def execute(self, uow: AbstractUnitOfWork) -> list[ReadCategorySchema]: ...


@dataclass
class FetchCategoriesUseCase(AbstractFetchCategoriesUseCase):

    category_service: AbstractCategoryService

    async def execute(self, uow: AbstractUnitOfWork):
        async with uow:
            return await self.category_service.list_all(uow=uow)
