from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from app.schemas.filters import PaginationIn
from app.schemas.messages import ReadMessageSchema
from app.services.messages import AbstractMessageService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchMessagesUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        pagination_in: PaginationIn,
        uow: AbstractUnitOfWork,
    ) -> list[ReadMessageSchema]: ...


@dataclass
class FetchMessagesUseCase(AbstractFetchMessagesUseCase):

    messages_service: AbstractMessageService

    async def execute(
        self,
        pagination_in: PaginationIn,
        uow: AbstractUnitOfWork,
    ) -> list[ReadMessageSchema]:
        async with uow:
            return await self.messages_service.list_all_messages(
                pagination_in=pagination_in,
                uow=uow,
            )
