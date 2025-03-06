from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from app.schemas.messages import ReadMessageSchema
from app.services.messages import AbstractMessageService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchMessageUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        message_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadMessageSchema: ...


@dataclass
class FetchMessageUseCase(AbstractFetchMessageUseCase):

    messages_service: AbstractMessageService

    async def execute(
        self,
        message_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadMessageSchema:
        async with uow:
            return await self.messages_service.get_message(
                message_id=message_id,
                uow=uow,
            )
