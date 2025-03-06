from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.messages import CreateMessageSchema, ReadMessageSchema
from app.services.messages import AbstractMessageService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractCreateMessageUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        message_in: CreateMessageSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadMessageSchema: ...


@dataclass
class CreateMessageUseCase(AbstractCreateMessageUseCase):
    message_service: AbstractMessageService

    async def execute(
        self,
        message_in: CreateMessageSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadMessageSchema:
        async with uow:
            return await self.message_service.create_message(
                message_in=message_in,
                uow=uow,
            )
