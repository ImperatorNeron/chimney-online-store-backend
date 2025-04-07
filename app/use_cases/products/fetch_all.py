from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.api_response import ListPaginatedResponse
from app.schemas.filters import PaginationIn, PaginationOut, ProductFiltersSchema, SortOrderSchema
from app.schemas.products import ReadPreviewProductSchema
from app.services.products import AbstractProductService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchProductsUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        filters: ProductFiltersSchema,
        sort_params: SortOrderSchema,
        uow: AbstractUnitOfWork,
        pagination_in: PaginationIn,
    ) -> ListPaginatedResponse[ReadPreviewProductSchema]: ...


@dataclass
class FetchProductsUseCase(AbstractFetchProductsUseCase):

    product_service: AbstractProductService

    async def execute(
        self,
        filters: ProductFiltersSchema,
        sort_params: SortOrderSchema,
        uow: AbstractUnitOfWork,
        pagination_in: PaginationIn,
    ) -> ListPaginatedResponse[ReadPreviewProductSchema]:
        async with uow:
            product = await self.product_service.list_all(
                filters=filters,
                sort_params=sort_params,
                pagination_in=pagination_in,
                uow=uow,
            )
            count = await self.product_service.get_products_count(
                uow=uow,
                filters=filters,
            )
            return ListPaginatedResponse(
                items=product,
                pagination=PaginationOut(
                    offset=pagination_in.offset,
                    limit=pagination_in.limit,
                    total=count,
                ),
            )
