from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.services.products import AbstractProductService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractDeleteUniqueProductUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        unique_product_id: int,
        uow: AbstractUnitOfWork,
    ) -> None: ...


@dataclass
class DeleteUniqueProductUseCase(AbstractDeleteUniqueProductUseCase):

    product_service: AbstractProductService

    async def execute(
        self,
        unique_product_id: int,
        uow: AbstractUnitOfWork,
    ) -> None:
        async with uow:
            await self.product_service.delete_unique(
                unique_product_id=unique_product_id,
                uow=uow,
            )
