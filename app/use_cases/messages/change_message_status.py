import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.messages import (
    ChangeMessageStatusSchema,
    ReadMessageSchema,
)
from app.services.messages import AbstractMessageService
from app.utils.unit_of_work import AbstractUnitOfWork


logger = logging.getLogger(__name__)


class AbstractChangeMessageStatusUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        message_id: int,
        message_in: ChangeMessageStatusSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadMessageSchema: ...


@dataclass
class ChangeMessageStatusUseCase(AbstractChangeMessageStatusUseCase):
    message_service: AbstractMessageService

    async def execute(
        self,
        message_id: int,
        message_in: ChangeMessageStatusSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadMessageSchema:
        logger.info(
            f"ChangeMessageStatusUseCase: change message status for message_id={message_id}."
        )

        async with uow:
            return await self.message_service.change_message_status(
                message_id=message_id,
                message_in=message_in,
                uow=uow,
            )
