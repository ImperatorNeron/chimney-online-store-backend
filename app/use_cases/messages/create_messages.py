import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.messages import CreateMessageSchema, ReadMessageSchema
from app.services.messages import AbstractMessageService
from app.utils.pii import mask_generic, mask_phone
from app.utils.unit_of_work import AbstractUnitOfWork


logger = logging.getLogger(__name__)


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
        logger.info(
            f"CreateMessageUseCase: create message for username={mask_generic(message_in.user_name)}, "
            f"phone={mask_phone(message_in.phone_number)}",
        )

        async with uow:
            return await self.message_service.create(
                item_in=message_in,
                uow=uow,
            )
