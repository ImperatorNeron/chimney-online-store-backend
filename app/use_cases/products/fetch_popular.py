from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.api_response import ListPaginatedResponse
from app.schemas.filters import PaginationIn, PaginationOut
from app.schemas.products import ReadPreviewProductSchema
from app.services.products import AbstractProductService
from app.services.website_settings import AbstractWebSiteSettingsService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchPopularProductsUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        uow: AbstractUnitOfWork,
        pagination_in: PaginationIn,
    ) -> ListPaginatedResponse[ReadPreviewProductSchema]: ...


@dataclass
class FetchPopularProductsUseCase(AbstractFetchPopularProductsUseCase):

    product_service: AbstractProductService
    settings_service: AbstractWebSiteSettingsService

    async def execute(
        self,
        uow: AbstractUnitOfWork,
        pagination_in: PaginationIn,
    ) -> ListPaginatedResponse[ReadPreviewProductSchema]:
        async with uow:
            ws = await self.settings_service.get_settings(uow=uow)
            results = await self.product_service.get_popular_products(
                uow=uow,
                pagination_in=pagination_in,
                website_settings=ws,
            )
            return ListPaginatedResponse(
                items=results,
                pagination=PaginationOut(
                    offset=pagination_in.offset,
                    limit=pagination_in.limit,
                    total=len(results),
                ),
            )
