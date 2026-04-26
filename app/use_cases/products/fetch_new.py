from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.api_response import ListPaginatedResponse
from app.schemas.filters import PaginationIn, PaginationOut
from app.schemas.products import ReadPreviewProductSchema
from app.services.products import AbstractProductService
from app.services.website_settings import AbstractWebSiteSettingsService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchNewProductsUseCase(ABC):

    @abstractmethod
    async def execute(
        self, pagination_in: PaginationIn, uow: AbstractUnitOfWork,
    ) -> ListPaginatedResponse[ReadPreviewProductSchema]: ...


@dataclass
class FetchNewProductsUseCase(AbstractFetchNewProductsUseCase):

    product_service: AbstractProductService
    settings_service: AbstractWebSiteSettingsService

    async def execute(
        self, pagination_in: PaginationIn, uow: AbstractUnitOfWork,
    ) -> ListPaginatedResponse[ReadPreviewProductSchema]:
        async with uow:
            ws = await self.settings_service.get_settings(uow=uow)
            items = await self.product_service.get_new_products(
                uow=uow,
                limit=pagination_in.limit,
                offset=pagination_in.offset,
                website_settings=ws,
            )
            count = await self.product_service.count(uow=uow, filters={"discount_percentage": 0})
            return ListPaginatedResponse(
                items=items,
                pagination=PaginationOut(
                    offset=pagination_in.offset,
                    limit=pagination_in.limit,
                    total=count,
                ),
            )
