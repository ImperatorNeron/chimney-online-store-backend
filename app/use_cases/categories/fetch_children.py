from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.categories import ReadCategorySchema
from app.services.categories import AbstractCategoryService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchChildCategoriesUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        parent_ids: list[int],
        uow: AbstractUnitOfWork,
    ) -> list[ReadCategorySchema]: ...


@dataclass
class FetchChildCategoriesUseCase(AbstractFetchChildCategoriesUseCase):

    category_service: AbstractCategoryService

    async def execute(
        self,
        parent_ids: list[int],
        uow: AbstractUnitOfWork,
    ) -> list[ReadCategorySchema]:
        async with uow:
            return await self.category_service.get_children_by_parent_ids(
                parent_ids=parent_ids,
                uow=uow,
            )

