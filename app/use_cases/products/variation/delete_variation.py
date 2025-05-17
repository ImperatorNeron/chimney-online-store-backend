from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.services.products import AbstractProductService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractDeleteProductVariationUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        product_variation_id: int,
        uow: AbstractUnitOfWork,
    ) -> None: ...


@dataclass
class DeleteProductVariationUseCase(AbstractDeleteProductVariationUseCase):

    product_service: AbstractProductService

    async def execute(
        self,
        product_variation_id: int,
        uow: AbstractUnitOfWork,
    ) -> None:
        async with uow:
            await self.product_service.delete_variation(
                product_variation_id=product_variation_id,
                uow=uow,
            )
