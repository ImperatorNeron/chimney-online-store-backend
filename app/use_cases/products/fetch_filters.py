from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.filters import ProductFiltersSchema
from app.schemas.products import ReadFiltersSchema
from app.services.products import AbstractProductService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchFiltersUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        slug: str,
        text: str,
        uow: AbstractUnitOfWork,
    ) -> ReadFiltersSchema: ...


@dataclass
class FetchFiltersUseCase(AbstractFetchFiltersUseCase):

    product_service: AbstractProductService

    async def execute(
        self,
        slug: str,
        text: str,
        uow: AbstractUnitOfWork,
    ) -> ReadFiltersSchema:
        async with uow:
            initial_filters = ProductFiltersSchema(
                category_slug=slug,
                text=text,
            )

            filters = await self.product_service.get_filters(
                filters=initial_filters,
                uow=uow,
            )
            price_range = await self.product_service.get_min_max_price(
                filters=initial_filters,
                uow=uow,
            )
            return {**filters, **price_range}
