from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.api_response import ListPaginatedResponse
from app.schemas.filters import PaginationIn, PaginationOut
from app.schemas.products import ReadPreviewProductSchema
from app.services.products import AbstractProductService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchProductsUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        uow: AbstractUnitOfWork,
        pagination_in: PaginationIn,
    ) -> ListPaginatedResponse[ReadPreviewProductSchema]: ...


@dataclass
class FetchProductsUseCase(AbstractFetchProductsUseCase):

    product_service: AbstractProductService

    async def execute(
        self,
        uow: AbstractUnitOfWork,
        pagination_in: PaginationIn,
    ) -> ListPaginatedResponse[ReadPreviewProductSchema]:
        async with uow:
            product = await self.product_service.list_all(
                pagination_in=pagination_in,
                uow=uow,
            )
            count = await self.product_service.get_total_products(uow=uow)
            return ListPaginatedResponse(
                items=product,
                pagination=PaginationOut(
                    offset=pagination_in.offset,
                    limit=pagination_in.limit,
                    total=count,
                ),
            )
