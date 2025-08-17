from abc import ABC, abstractmethod

from app.schemas.filters import MessageFiltersSchema, MessageSortOrderSchema, PaginationIn
from app.schemas.messages import ChangeMessageStatusSchema, CreateMessageSchema, ReadMessageSchema
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractMessageService(ABC):

    @abstractmethod
    async def list_all_messages(
        self,
        filters: MessageFiltersSchema,
        pagination_in: PaginationIn,
        sort_params: MessageSortOrderSchema,
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
    async def change_message_status(
        self,
        message_id: int,
        message_in: ChangeMessageStatusSchema,
        uow: AbstractUnitOfWork,
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
        filters: MessageFiltersSchema,
        pagination_in: PaginationIn,
        sort_params: MessageSortOrderSchema,
        uow: AbstractUnitOfWork,
    ) -> list[ReadMessageSchema]:
        order_by = (
            f"-{sort_params.field}"
            if sort_params.ordering == "desc"
            else sort_params.field
        )
        return await uow.messages.all(
            order_by=[order_by],
            limit=pagination_in.limit,
            offset=pagination_in.offset,
            filters=filters.model_dump(),
        )

    async def get_total_messages(
        self,
        filters: MessageFiltersSchema,
        uow: AbstractUnitOfWork,
    ) -> int:
        return await uow.messages.count(**filters.model_dump())

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

    async def change_message_status(
        self,
        message_id: int,
        message_in: ChangeMessageStatusSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadMessageSchema:
        return await uow.messages.update(id=message_id, item_in=message_in)

    async def delete_message(
        self,
        message_id: int,
        uow: AbstractUnitOfWork,
    ) -> None:
        await uow.messages.delete(id=message_id)
