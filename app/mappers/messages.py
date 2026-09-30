from app.mappers.base import BaseReadMapper, BaseUpsertMapper
from app.models.messages import Message
from app.schemas.messages import CreateMessageSchema, ReadMessageSchema, UpdateMessageStatusSchema


class MessageReadMapper(BaseReadMapper[Message, ReadMessageSchema]):

    @staticmethod
    def to_dto(orm_obj: Message) -> ReadMessageSchema:
        return ReadMessageSchema(
            id=orm_obj.id,
            user_name=orm_obj.user_name,
            phone_number=orm_obj.phone_number,
            message=orm_obj.message,
            created_at=orm_obj.created_at,
            status=orm_obj.status,
        )


class MessageCreateMapper(BaseUpsertMapper[Message, CreateMessageSchema]):
    pass


class MessageStatusUpdateMapper(BaseUpsertMapper[Message, UpdateMessageStatusSchema]):
    pass
