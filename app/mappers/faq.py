from app.mappers.base import BaseReadMapper, BaseUpsertMapper
from app.models.faq import FAQ
from app.schemas.faq import CreateFAQSchema, ReadFAQSchema, UpdadeFAQSchema


class FaqReadMapper(BaseReadMapper[FAQ, ReadFAQSchema]):

    @staticmethod
    def to_dto(orm_obj: FAQ) -> ReadFAQSchema:
        return ReadFAQSchema(
            id=orm_obj.id,
            question=orm_obj.question,
            answer=orm_obj.answer,
            youtube_url=orm_obj.youtube_url,
            embed_url=orm_obj.get_embed_url(),
        )


class FaqCreateMapper(BaseUpsertMapper[FAQ, CreateFAQSchema]):
    pass


class FaqUpdateMapper(BaseUpsertMapper[FAQ, UpdadeFAQSchema]):
    pass
