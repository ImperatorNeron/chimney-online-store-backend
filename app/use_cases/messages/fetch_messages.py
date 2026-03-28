from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.api_response import ListPaginatedResponse
from app.schemas.filters import MessageFiltersSchema, MessageSortOrderSchema, PaginationIn, PaginationOut
from app.schemas.messages import ReadMessageSchema
from app.services.messages import AbstractMessageService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchMessagesUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        filters: MessageFiltersSchema,
        sort_params: MessageSortOrderSchema,
        pagination_in: PaginationIn,
        uow: AbstractUnitOfWork,
    ) -> ListPaginatedResponse[ReadMessageSchema]: ...


@dataclass
class FetchMessagesUseCase(AbstractFetchMessagesUseCase):

    messages_service: AbstractMessageService

    async def execute(
        self,
        filters: MessageFiltersSchema,
        sort_params: MessageSortOrderSchema,
        pagination_in: PaginationIn,
        uow: AbstractUnitOfWork,
    ) -> ListPaginatedResponse[ReadMessageSchema]:
        async with uow:
            count = await self.messages_service.count(
                uow=uow,
                filters=filters,
            )
            items = await self.messages_service.list_all(
                pagination_in=pagination_in,
                filters=filters,
                order_by=sort_params,
                uow=uow,
            )
            return ListPaginatedResponse(
                items=items,
                pagination=PaginationOut(
                    offset=pagination_in.offset,
                    limit=pagination_in.limit,
                    total=count,
                ),
            )
