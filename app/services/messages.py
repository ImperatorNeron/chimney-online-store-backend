from typing import Type

from app.mappers.messages import MessageCreateMapper, MessageReadMapper, MessageStatusUpdateMapper
from app.schemas.messages import CreateMessageSchema, ReadMessageSchema, UpdateMessageStatusSchema
from app.services.base import AbstractCRUDService, CRUDService


class AbstractMessageService(
    AbstractCRUDService[
        ReadMessageSchema,
        CreateMessageSchema,
        UpdateMessageStatusSchema,
    ],
):
    pass


class MessageService(AbstractMessageService, CRUDService):
    repository_name: str = "messages"
    _read_mapper: Type[MessageReadMapper] = MessageReadMapper
    read_mapper = read_create_mapper = read_update_mapper = _read_mapper
    create_mapper: Type[MessageCreateMapper] = MessageCreateMapper
    update_mapper: Type[MessageStatusUpdateMapper] = MessageStatusUpdateMapper
