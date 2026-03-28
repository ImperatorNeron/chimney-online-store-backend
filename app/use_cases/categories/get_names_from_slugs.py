from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.services.categories import AbstractCategoryService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchNamesFromSlugsUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        slugs: list[str],
        uow: AbstractUnitOfWork,
        # TODO: change to ReadCategoryNameSlugSchema
    ) -> list[list[str, str]]: ...


@dataclass
class FetchNamesFromSlugsUseCase(AbstractFetchNamesFromSlugsUseCase):

    category_service: AbstractCategoryService

    async def execute(
        self,
        slugs: list[str],
        uow: AbstractUnitOfWork,
    ) -> list[list[str, str]]:
        async with uow:
            results = await self.category_service.get_category_names_from_slugs(
                slugs=slugs,
                uow=uow,
            )
            return [[category.name, category.slug] for category in results]
