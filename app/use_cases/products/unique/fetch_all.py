from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.api_response import ListPaginatedResponse
from app.schemas.filters import PaginationIn, PaginationOut, UniqueProductFiltersSchema, UniqueProductSortOrderSchema
from app.schemas.products import ReadFullUniqueProductSchema
from app.services.unique_products import AbstractUniqueProductService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchUniqueProductsUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        filters: UniqueProductFiltersSchema,
        sort_params: UniqueProductSortOrderSchema,
        pagination_in: PaginationIn,
        uow: AbstractUnitOfWork,
    ) -> ListPaginatedResponse[ReadFullUniqueProductSchema]: ...


@dataclass
class FetchUniqueProductsUseCase(AbstractFetchUniqueProductsUseCase):

    unique_product_service: AbstractUniqueProductService

    async def execute(
        self,
        filters: UniqueProductFiltersSchema,
        sort_params: UniqueProductSortOrderSchema,
        pagination_in: PaginationIn,
        uow: AbstractUnitOfWork,
    ) -> ListPaginatedResponse[ReadFullUniqueProductSchema]:
        async with uow:
            products = await self.unique_product_service.list_all(
                filters=filters,
                order_by=sort_params,
                pagination_in=pagination_in,
                uow=uow,
            )
            count = await self.unique_product_service.count(
                filters=filters,
                uow=uow,
            )
            return ListPaginatedResponse(
                items=products,
                pagination=PaginationOut(
                    offset=pagination_in.offset,
                    limit=pagination_in.limit,
                    total=count,
                ),
            )
