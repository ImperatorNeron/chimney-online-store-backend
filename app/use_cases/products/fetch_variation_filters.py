from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.filters import FiltersSchema
from app.services.products import AbstractProductService
from app.services.unique_products import AbstractUniqueProductService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchVariationFiltersUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        product_slug: str,
        uow: AbstractUnitOfWork,
    ) -> FiltersSchema: ...


@dataclass
class FetchVariationFiltersUseCase(AbstractFetchVariationFiltersUseCase):

    product_service: AbstractProductService
    unique_product_service: AbstractUniqueProductService

    async def execute(
        self,
        product_slug: str,
        uow: AbstractUnitOfWork,
    ) -> FiltersSchema:
        async with uow:
            unique_product = await self.unique_product_service.get_one(
                uow=uow, conditions={"slug": product_slug},
            )
            return await self.product_service.get_variation_filters(
                uow=uow, product_id=unique_product.id,
            )
