from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.api_response import ListPaginatedResponse
from app.schemas.filters import PaginationIn, PaginationOut
from app.schemas.products import ReadUniqueProductSchema
from app.services.products import AbstractProductService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchUniqueProductsUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        uow: AbstractUnitOfWork,
        pagination_in: PaginationIn,
    ) -> ListPaginatedResponse[ReadUniqueProductSchema]: ...


@dataclass
class FetchUniqueProductsUseCase(AbstractFetchUniqueProductsUseCase):

    product_service: AbstractProductService

    async def execute(
        self,
        uow: AbstractUnitOfWork,
        pagination_in: PaginationIn,
    ) -> ListPaginatedResponse[ReadUniqueProductSchema]:
        async with uow:
            products = await self.product_service.list_all_unique(
                pagination_in=pagination_in,
                uow=uow,
            )
            count = await self.product_service.get_unique_products_count(
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
