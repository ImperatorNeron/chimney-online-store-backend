from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.api_response import ListPaginatedResponse
from app.schemas.filters import CustomerFiltersSchema, CustomerSortOrderSchema, PaginationIn, PaginationOut
from app.schemas.orders import ReadCustomerSchema
from app.services.orders import AbstractOrderService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchCustomersUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        filters: CustomerFiltersSchema,
        sort_params: CustomerSortOrderSchema,
        pagination_in: PaginationIn,
        uow: AbstractUnitOfWork,
    ) -> ListPaginatedResponse[ReadCustomerSchema]: ...


@dataclass
class FetchCustomersUseCase(AbstractFetchCustomersUseCase):
    order_service: AbstractOrderService

    async def execute(
        self,
        filters: CustomerFiltersSchema,
        sort_params: CustomerSortOrderSchema,
        pagination_in: PaginationIn,
        uow: AbstractUnitOfWork,
    ) -> ListPaginatedResponse[ReadCustomerSchema]:
        async with uow:
            items = await self.order_service.get_customers(
                uow=uow,
                filters=filters,
                sort_params=sort_params,
                limit=pagination_in.limit,
                offset=pagination_in.offset,
            )
            count = await self.order_service.get_customers_count(
                uow=uow, filters=filters,
            )
            return ListPaginatedResponse(
                items=items,
                pagination=PaginationOut(
                    offset=pagination_in.offset,
                    limit=pagination_in.limit,
                    total=count,
                ),
            )
