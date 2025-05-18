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
    async def get_total_messages(
        self,
        uow: AbstractUnitOfWork,
    ) -> int: ...

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

    @abstractmethod
    async def delete_message(
        self,
        message_id: int,
        uow: AbstractUnitOfWork,
    ) -> None: ...


class MessageService(AbstractMessageService):

    async def list_all_messages(
        self,
        pagination_in: PaginationIn,
        uow: AbstractUnitOfWork,
    ) -> list[ReadMessageSchema]:
        return await uow.messages.all(
            order_by=["-created_at"],
            limit=pagination_in.limit,
            offset=pagination_in.offset,
        )

    async def get_total_messages(
        self,
        uow: AbstractUnitOfWork,
    ) -> int:
        return await uow.messages.count()

    async def get_message(
        self,
        message_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadMessageSchema:
        return await uow.messages.get(id=message_id)

    async def create_message(
        self,
        uow: AbstractUnitOfWork,
        message_in: CreateMessageSchema,
    ) -> ReadMessageSchema:
        return await uow.messages.create(item_in=message_in)

    async def delete_message(
        self,
        message_id: int,
        uow: AbstractUnitOfWork,
    ) -> None:
        await uow.messages.delete(id=message_id)
