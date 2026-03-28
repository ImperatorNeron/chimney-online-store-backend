import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.messages import ReadMessageSchema, UpdateMessageStatusSchema
from app.services.messages import AbstractMessageService
from app.utils.unit_of_work import AbstractUnitOfWork


logger = logging.getLogger(__name__)


class AbstractChangeMessageStatusUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        message_id: int,
        message_in: UpdateMessageStatusSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadMessageSchema: ...


@dataclass
class ChangeMessageStatusUseCase(AbstractChangeMessageStatusUseCase):
    message_service: AbstractMessageService

    async def execute(
        self,
        message_id: int,
        message_in: UpdateMessageStatusSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadMessageSchema:
        logger.info(
            f"ChangeMessageStatusUseCase: change message status for message_id={message_id}.",
        )

        async with uow:
            return await self.message_service.update(
                item_id=message_id,
                item_in=message_in,
                uow=uow,
            )
