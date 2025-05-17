from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.api_response import ListPaginatedResponse
from app.schemas.filters import PaginationIn, PaginationOut
from app.schemas.products import ReadProductVariationSchema
from app.services.products import AbstractProductService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchProductVariationsUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        uow: AbstractUnitOfWork,
        unique_product_id: int,
        pagination_in: PaginationIn,
    ) -> ListPaginatedResponse[ReadProductVariationSchema]: ...


@dataclass
class FetchProductVariationsUseCase(AbstractFetchProductVariationsUseCase):

    product_service: AbstractProductService

    async def execute(
        self,
        uow: AbstractUnitOfWork,
        unique_product_id: int,
        pagination_in: PaginationIn,
    ) -> ListPaginatedResponse[ReadProductVariationSchema]:
        async with uow:
            products = await self.product_service.list_variations_by_product_id(
                pagination_in=pagination_in,
                unique_product_id=unique_product_id,
                uow=uow,
            )
            count = await self.product_service.count_variations_by_product_id(
                unique_product_id=unique_product_id,
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
