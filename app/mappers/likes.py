from app.mappers.base import BaseReadMapper, BaseUpsertMapper
from app.models.likes import Like
from app.schemas.likes import CreateLikeSchema, ReadLikeSchema


class LikeReadMapper(BaseReadMapper[Like, ReadLikeSchema]):

    @staticmethod
    def to_dto(orm_obj: Like) -> ReadLikeSchema:
        return ReadLikeSchema(
            id=orm_obj.id,
            user_id=orm_obj.user_id,
            product_id=orm_obj.product_id,
        )


class LikeCreateMapper(BaseUpsertMapper[Like, CreateLikeSchema]):
    pass
