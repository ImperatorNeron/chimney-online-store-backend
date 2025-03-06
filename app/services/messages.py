from abc import ABC, abstractmethod

from app.schemas.filters import PaginationIn
from app.schemas.messages import CreateMessageSchema, ReadMessageSchema
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractMessageService(ABC):

    @abstractmethod
    async def list_all_messages(
        self,
        pagination_in: PaginationIn,
        uow: AbstractUnitOfWork,
    ) -> list[ReadMessageSchema]: ...

    @abstractmethod
    async def get_message(
        self,
        message_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadMessageSchema: ...

    @abstractmethod
    async def create_message(
        self,
        uow: AbstractUnitOfWork,
        message_in: CreateMessageSchema,
    ) -> ReadMessageSchema: ...


class MessageService(AbstractMessageService):

    async def list_all_messages(
        self,
        pagination_in: PaginationIn,
        uow: AbstractUnitOfWork,
    ) -> list[ReadMessageSchema]:
        return await uow.messages.fetch_all(pagination_in=pagination_in)

    async def get_message(
        self,
        message_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadMessageSchema:
        return await uow.messages.fetch_by_id(item_id=message_id)

    async def create_message(
        self,
        uow: AbstractUnitOfWork,
        message_in: CreateMessageSchema,
    ) -> ReadMessageSchema:
        return await uow.messages.create(item_in=message_in)
