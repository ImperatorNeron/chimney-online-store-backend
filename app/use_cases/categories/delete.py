from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.services.categories import AbstractCategoryService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractDeleteCategoryUseCase(ABC):

    @abstractmethod
    async def execute(self, category_id: int, uow: AbstractUnitOfWork) -> None: ...


@dataclass
class DeleteCategoryUseCase(AbstractDeleteCategoryUseCase):

    category_service: AbstractCategoryService

    async def execute(self, category_id: int, uow: AbstractUnitOfWork):
        async with uow:
            await self.category_service.delete(item_id=category_id, uow=uow)
