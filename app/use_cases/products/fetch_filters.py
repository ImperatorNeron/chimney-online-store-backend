from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.filters import CatalogFiltersSchema, ProductFiltersSchema
from app.schemas.products import ReadFiltersSchema
from app.services.products import AbstractProductService
from app.services.website_settings import AbstractWebSiteSettingsService
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
    settings_service: AbstractWebSiteSettingsService

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

            ws = await self.settings_service.get_settings(uow=uow)
            multiplier = (1 - ws.manufacturer_discount / 100) * (1 + ws.seller_markup / 100)

            # This is correct Schema, but everything else is bad. This is just to save functionality
            # TODO: need to return just schema(right one) and not dict
            return CatalogFiltersSchema(
                **filters.model_dump(),
                min_price=round(price_range.min_price * multiplier) if price_range.min_price else 0,
                max_price=round(price_range.max_price * multiplier) if price_range.max_price else 0,
            ).model_dump()
