from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.api_response import ListPaginatedResponse
from app.schemas.filters import PaginationIn, PaginationOut
from app.schemas.messages import ReadMessageSchema
from app.services.messages import AbstractMessageService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchMessagesUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        pagination_in: PaginationIn,
        uow: AbstractUnitOfWork,
    ) -> ListPaginatedResponse[ReadMessageSchema]: ...


@dataclass
class FetchMessagesUseCase(AbstractFetchMessagesUseCase):

    messages_service: AbstractMessageService

    async def execute(
        self,
        pagination_in: PaginationIn,
        uow: AbstractUnitOfWork,
    ) -> ListPaginatedResponse[ReadMessageSchema]:
        async with uow:
            count = await self.messages_service.get_total_messages(uow=uow)
            items = await self.messages_service.list_all_messages(
                pagination_in=pagination_in,
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
