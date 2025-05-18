from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.services.messages import AbstractMessageService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractDeleteMessageUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        message_id: int,
        uow: AbstractUnitOfWork,
    ) -> None: ...


@dataclass
class DeleteMessageUseCase(AbstractDeleteMessageUseCase):

    messages_service: AbstractMessageService

    async def execute(
        self,
        message_id: int,
        uow: AbstractUnitOfWork,
    ):
        async with uow:
            await self.messages_service.delete_message(
                message_id=message_id,
                uow=uow,
            )
