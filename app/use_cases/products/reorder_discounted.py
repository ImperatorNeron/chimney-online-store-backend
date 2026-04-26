from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.products import ReorderDiscountedItemSchema
from app.services.products import AbstractProductService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractReorderDiscountedUseCase(ABC):

    @abstractmethod
    async def execute(
        self, items: list[ReorderDiscountedItemSchema], uow: AbstractUnitOfWork,
    ) -> None: ...


@dataclass
class ReorderDiscountedUseCase(AbstractReorderDiscountedUseCase):

    product_service: AbstractProductService

    async def execute(
        self, items: list[ReorderDiscountedItemSchema], uow: AbstractUnitOfWork,
    ) -> None:
        async with uow:
            for entry in items:
                await self.product_service.update_discount_sort_order(
                    uow=uow,
                    variation_id=entry.variation_id,
                    sort_order=entry.sort_order,
                )
